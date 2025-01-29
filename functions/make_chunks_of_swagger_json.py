# TODO : send to general_utils / api_utils
def create_chunk(swagger_data, operations):
    is_openapi_3 = 'openapi' in swagger_data
    
    used_schemas = set()
    required_security_schemes = set()

    for operation_info in operations:
        path_key, method, operation = operation_info

        if is_openapi_3:
            request_body = operation.get('requestBody', {})
            if 'content' in request_body:
                for content in request_body['content'].values():
                    schema = content.get('schema', {})
                    ref = schema.get('items', {}).get('$ref', schema.get('$ref', None))
                    if ref:
                        used_schemas.add(ref.split('/')[-1])

            responses = operation.get('responses', {})
            for response in responses.values():
                content = response.get('content', {})
                for media_type in content.values():
                    schema = media_type.get('schema', {})
                    ref = schema.get('items', {}).get('$ref', schema.get('$ref', None))
                    if ref:
                        used_schemas.add(ref.split('/')[-1])
        else:
            parameters = operation.get('parameters', [])
            for param in parameters:
                schema = param.get('schema', {})
                ref = schema.get('items', {}).get('$ref', schema.get('$ref', None))
                if ref:
                    used_schemas.add(ref.split('/')[-1])

            responses = operation.get('responses', {})
            for response in responses.values():
                schema = response.get('schema', {})
                ref = schema.get('items', {}).get('$ref', schema.get('$ref', None))
                if ref:
                    used_schemas.add(ref.split('/')[-1])

        security = operation.get('security', [])
        for requirement in security:
            required_security_schemes.update(requirement.keys())

    chunk = {
        'swagger' if not is_openapi_3 else 'openapi': '2.0' if not is_openapi_3 else swagger_data.get('openapi', '3.0.0'),
        'info': swagger_data.get('info', {}),
        'host': swagger_data.get('host', '') if not is_openapi_3 else '',
        'basePath': swagger_data.get('basePath', '') if not is_openapi_3 else '',
        'schemes': swagger_data.get('schemes', []) if not is_openapi_3 else [],
        'servers': swagger_data.get('servers', []) if is_openapi_3 else [],
        'security': swagger_data.get('security', []),
        'paths': {path_key: {method: operation} for path_key, method, operation in operations},
        'definitions' if not is_openapi_3 else 'components': {
            schema_key: swagger_data.get('definitions' if not is_openapi_3 else 'components', {}).get(schema_key)
            for schema_key in used_schemas if schema_key in swagger_data.get('definitions' if not is_openapi_3 else 'components', {})
        },
        'securityDefinitions' if not is_openapi_3 else 'securitySchemes': {
            scheme_key: swagger_data.get('securityDefinitions' if not is_openapi_3 else 'securitySchemes', {}).get(scheme_key)
            for scheme_key in required_security_schemes if scheme_key in swagger_data.get('securityDefinitions' if not is_openapi_3 else 'securitySchemes', {})
        }
    }
    return chunk

def divide_swagger_json(swagger_data):
    chunks_by_tag = {}

    paths = swagger_data.get('paths', {})
    
    for path_key, path_item in paths.items():
        for method, operation in path_item.items():
            tags = operation.get('tags') or ['common']  # Default to 'common' if no tags
            for tag in tags:
                chunks_by_tag.setdefault(tag, []).append((path_key, method, operation))

    chunks = []
    for tag, operations in chunks_by_tag.items():
        chunk = create_chunk(swagger_data, operations)
        chunks.append({tag: chunk})

    return chunks

def create_method_chunks(swagger_data, operations):
    method_dict = {'get': [], 'post': [], 'put': [], 'delete': [], 'patch': []}
    # Organize operations by HTTP method
    for operation_info in operations:
        path_key, method, operation = operation_info
        if method in method_dict:
            method_dict[method].append((path_key, method, operation))

    # Create chunks for each method
    chunks = {}
    for method, ops in method_dict.items():
        if ops:  # Only create a chunk if there are operations for this method
            chunk = create_chunk(swagger_data, ops)
            chunks[method] = chunk
    return chunks

def divide_swagger_json_by_tag_and_method(swagger_data):
    chunks_by_tag = {}

    paths = swagger_data.get('paths', {})
    
    # First divide by tag
    for path_key, path_item in paths.items():
        for method, operation in path_item.items():
            tags = operation.get('tags', ['common'])  # Use 'common' if no tags are specified
            for tag in tags:
                chunks_by_tag.setdefault(tag, []).append((path_key, method, operation))

    # Now divide each tag's operations by method
    final_chunks = {}
    for tag, operations in chunks_by_tag.items():
        method_chunks = create_method_chunks(swagger_data, operations)
        final_chunks[tag] = method_chunks

    return final_chunks