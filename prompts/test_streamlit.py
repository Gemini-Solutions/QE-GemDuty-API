# import streamlit as st
# import time

# "Starting a long computation..."

# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)

# for i in range(100):
#     # Update the progress bar with each iteration.
#     latest_iteration.text(f"Iteration {i+1}")
#     bar.progress(i + 1)
#     time.sleep(0.1)

# "...and now we're done!"

import streamlit as st
import pandas as pd

# Sample data
data = {
    "Column 1": ["Row 1", "Row 2", "Row 3"],
    "Column 2": ["Data 1", "Data 2", "Data 3"],
}

# Create a DataFrame
df = pd.DataFrame(data)

# Display the table with two columns of different widths
col1, col2 = st.columns([1, 2])  # Relative widths, change 1 and 2 to your preference

with col1:
    st.write("### Column 1")
    for row in df["Column 1"]:
        st.write(row)

with col2:
    st.write("### Column 2")
    for row in df["Column 2"]:
        st.write(row)
