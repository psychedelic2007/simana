import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import base64
import io
import seaborn as sns

def parse_xvg(file_path):
    x_data = []
    y_data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('@') or line.startswith('#'):
                continue
            columns = line.strip().split()
            x_data.append(float(columns[0])/1000)
            y_data.append(float(columns[1]))
    return x_data, y_data

def calculate_hbond(uploaded_files, custom_labels):
    all_x_data = []
    all_y_data = []
    labels = []

    for i, uploaded_file in enumerate(uploaded_files):
        label = custom_labels[i] if custom_labels[i] else uploaded_file.name
        labels.append(label)
        
        with open("temp.xvg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        x_data, y_data = parse_xvg("temp.xvg")
        all_x_data.append(x_data)
        all_y_data.append(y_data)
    
    return all_x_data, all_y_data, labels

def plot_hbond(all_x_data, all_y_data, labels, customizations):
    fig, ax = plt.subplots(figsize=(15, 6))
    for i in range(len(all_x_data)):
        ax.plot(all_x_data[i], all_y_data[i], label=labels[i], color=customizations['colors'][i], linewidth=customizations['linewidth'])
    
    ax.set_xlabel(customizations['x_label'], fontsize=customizations['x_label_size'])
    ax.set_ylabel(customizations['y_label'], fontsize=customizations['y_label_size'])
    ax.set_title(f'Hydrogen Bond Analysis')
    ax.legend()
    
    ax.tick_params(axis='x', labelsize=customizations['tick_size'], rotation=customizations['x_tick_rotation'])
    ax.tick_params(axis='y', labelsize=customizations['tick_size'])
    ax.xaxis.set_major_locator(plt.MultipleLocator(customizations['x_tick_gap']))
    ax.yaxis.set_major_locator(plt.MultipleLocator(customizations['y_tick_gap']))
    ax.set_xlim(customizations['x_min'], customizations['x_max'])
    ax.set_ylim(customizations['y_min'], customizations['y_max'])
    
    return fig

def plot_distribution(all_y_data, labels, customizations):
    fig, ax = plt.subplots(figsize=(15, 6))
    for i, y_data in enumerate(all_y_data):
        sns.kdeplot(y_data, ax=ax, label=labels[i], color=customizations['colors'][i], fill=True, alpha=customizations['alpha'])
    
    ax.set_xlabel(customizations['x_label'], fontsize=customizations['x_label_size'])
    ax.set_ylabel(customizations['y_label'], fontsize=customizations['y_label_size'])
    ax.set_title('Hydrogen Bond Distribution')
    ax.legend()
    
    ax.tick_params(axis='x', labelsize=customizations['tick_size'], rotation=customizations['x_tick_rotation'])
    ax.tick_params(axis='y', labelsize=customizations['tick_size'])
    ax.xaxis.set_major_locator(plt.MultipleLocator(customizations['x_tick_gap']))
    ax.yaxis.set_major_locator(plt.MultipleLocator(customizations['y_tick_gap']))
    ax.set_xlim(customizations['x_min'], customizations['x_max'])
    ax.set_ylim(customizations['y_min'], customizations['y_max'])
    
    return fig

def get_download_link(fig, plot_name):
    format_options = ['PDF', 'PNG', 'SVG', 'EPS', 'JPG']
    format_selected = st.selectbox(f'Select download format for {plot_name}:', format_options, key=f"{plot_name}_format")
    
    if format_selected:
        buf = io.BytesIO()
        fig.savefig(buf, format=format_selected.lower())
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        href = f'<a href="data:application/{format_selected.lower()};base64,{b64}" download="{plot_name}.{format_selected.lower()}">Download</a>'
        return href
    return None
    
def hbond():
    st.title("Hydrogen Bond Analysis")

    if 'customizations_curve' not in st.session_state:
        st.session_state.customizations_curve = {
            'x_label': "Time (ns)",
            'y_label': "Hydrogen Bonds",
            'x_label_size': 12,
            'y_label_size': 12,
            'tick_size': 10,
            'x_tick_gap': 10,
            'y_tick_gap': 0.1,
            'linewidth': 1.5,
            'x_tick_rotation': 0,
            'colors': ["#000000"],
            'x_min': None,
            'x_max': None,
            'y_min': None,
            'y_max': None,
        }

    if 'customizations_dist' not in st.session_state:
        st.session_state.customizations_dist = {
            'x_label': "Hydrogen Bonds",
            'y_label': "Frequency",
            'x_label_size': 12,
            'y_label_size': 12,
            'tick_size': 10,
            'x_tick_gap': 0.1,
            'y_tick_gap': 100,
            'x_tick_rotation': 0,
            'colors': ["#000000"],
            'alpha': 0.5,
            'x_min': None,
            'x_max': None,
            'y_min': None,
            'y_max': None,
        }

    if 'data' not in st.session_state:
        st.session_state.data = None

    num_files = st.number_input('Enter number of files to upload', min_value=1, max_value=10, value=1, key='num_files')
    
    uploaded_files = []
    custom_labels = []
    for i in range(num_files):
        uploaded_file = st.file_uploader(f"Upload .xvg file {i+1}", type=['xvg'], key=f'file_{i}')
        label = st.text_input(f'Label for curve {i+1}', key=f'label_{i}')
        if uploaded_file:
            uploaded_files.append(uploaded_file)
            custom_labels.append(label)

    if st.button('Submit') and uploaded_files:
        all_x_data, all_y_data, labels = calculate_hbond(uploaded_files, custom_labels)
        st.session_state.data = {'all_x_data': all_x_data, 'all_y_data': all_y_data, 'labels': labels}
        st.session_state.customizations_curve['colors'] = ["#000000" for _ in range(num_files)]
        st.session_state.customizations_dist['colors'] = ["#000000" for _ in range(num_files)]

    st.sidebar.header("Hydrogen Bond Curve Plot Customization")
    st.session_state.customizations_curve['x_label'] = st.sidebar.text_input("X-axis Label (Curve)", value=st.session_state.customizations_curve['x_label'])
    st.session_state.customizations_curve['y_label'] = st.sidebar.text_input("Y-axis Label (Curve)", value=st.session_state.customizations_curve['y_label'])
    st.session_state.customizations_curve['x_label_size'] = st.sidebar.number_input("X-axis Label Size (Curve)", value=st.session_state.customizations_curve['x_label_size'])
    st.session_state.customizations_curve['y_label_size'] = st.sidebar.number_input("Y-axis Label Size (Curve)", value=st.session_state.customizations_curve['y_label_size'])
    st.session_state.customizations_curve['tick_size'] = st.sidebar.number_input("Tick Size (Curve)", value=st.session_state.customizations_curve['tick_size'])
    st.session_state.customizations_curve['x_tick_gap'] = st.sidebar.number_input("X-axis Tick Gap (Curve)", value=st.session_state.customizations_curve['x_tick_gap'])
    st.session_state.customizations_curve['y_tick_gap'] = st.sidebar.number_input("Y-axis Tick Gap (Curve)", value=st.session_state.customizations_curve['y_tick_gap'])
    st.session_state.customizations_curve['linewidth'] = st.sidebar.number_input("Line Width (Curve)", value=st.session_state.customizations_curve['linewidth'])
    st.session_state.customizations_curve['x_tick_rotation'] = st.sidebar.slider("X-axis Tick Rotation (Curve)", min_value=0, max_value=90, value=st.session_state.customizations_curve['x_tick_rotation'])
    st.session_state.customizations_curve['colors'] = [st.sidebar.color_picker(f"Color for curve {i+1}", value=st.session_state.customizations_curve['colors'][i] if i < len(st.session_state.customizations_curve['colors']) else "#000000", key=f'color_curve_{i}') for i in range(num_files)]
    st.session_state.customizations_curve['x_min'] = st.sidebar.number_input("X-axis Min (Curve)", value=st.session_state.customizations_curve['x_min'])
    st.session_state.customizations_curve['x_max'] = st.sidebar.number_input("X-axis Max (Curve)", value=st.session_state.customizations_curve['x_max'])
    st.session_state.customizations_curve['y_min'] = st.sidebar.number_input("Y-axis Min (Curve)", value=st.session_state.customizations_curve['y_min'])
    st.session_state.customizations_curve['y_max'] = st.sidebar.number_input("Y-axis Max (Curve)", value=st.session_state.customizations_curve['y_max'])

    st.sidebar.header("Hydrogen Bond Distribution Plot Customization")
    st.session_state.customizations_dist['x_label'] = st.sidebar.text_input("X-axis Label (Distribution)", value=st.session_state.customizations_dist['x_label'])
    st.session_state.customizations_dist['y_label'] = st.sidebar.text_input("Y-axis Label (Distribution)", value=st.session_state.customizations_dist['y_label'])
    st.session_state.customizations_dist['x_label_size'] = st.sidebar.number_input("X-axis Label Size (Distribution)", value=st.session_state.customizations_dist['x_label_size'])
    st.session_state.customizations_dist['y_label_size'] = st.sidebar.number_input("Y-axis Label Size (Distribution)", value=st.session_state.customizations_dist['y_label_size'])
    st.session_state.customizations_dist['tick_size'] = st.sidebar.number_input("Tick Size (Distribution)", value=st.session_state.customizations_dist['tick_size'])
    st.session_state.customizations_dist['x_tick_gap'] = st.sidebar.number_input("X-axis Tick Gap (Distribution)", value=st.session_state.customizations_dist['x_tick_gap'])
    st.session_state.customizations_dist['y_tick_gap'] = st.sidebar.number_input("Y-axis Tick Gap (Distribution)", value=st.session_state.customizations_dist['y_tick_gap'])
    st.session_state.customizations_dist['x_tick_rotation'] = st.sidebar.slider("X-axis Tick Rotation (Distribution)", min_value=0, max_value=90, value=st.session_state.customizations_dist['x_tick_rotation'])
    st.session_state.customizations_dist['colors'] = [st.sidebar.color_picker(f"Color for distribution {i+1}", value=st.session_state.customizations_dist['colors'][i] if i < len(st.session_state.customizations_dist['colors']) else "#000000", key=f'color_dist_{i}') for i in range(num_files)]
    st.session_state.customizations_dist['alpha'] = st.sidebar.slider("Fill Opacity (Distribution)", min_value=0.1, max_value=1.0, value=st.session_state.customizations_dist['alpha'], step=0.1)
    st.session_state.customizations_dist['x_min'] = st.sidebar.number_input("X-axis Min (Distribution)", value=st.session_state.customizations_dist['x_min'])
    st.session_state.customizations_dist['x_max'] = st.sidebar.number_input("X-axis Max (Distribution)", value=st.session_state.customizations_dist['x_max'])
    st.session_state.customizations_dist['y_min'] = st.sidebar.number_input("Y-axis Min (Distribution)", value=st.session_state.customizations_dist['y_min'])
    st.session_state.customizations_dist['y_max'] = st.sidebar.number_input("Y-axis Max (Distribution)", value=st.session_state.customizations_dist['y_max'])

    if st.session_state.data:
        all_x_data, all_y_data, labels = st.session_state.data['all_x_data'], st.session_state.data['all_y_data'], st.session_state.data['labels']
        
        # Plot Hydrogen Bond Curve
        fig_curve = plot_hbond(all_x_data, all_y_data, labels, st.session_state.customizations_curve)
        st.pyplot(fig_curve)
        link_curve = get_download_link(fig_curve, 'Hydrogen_Bond_Curve')
        if link_curve:
            st.markdown(link_curve, unsafe_allow_html=True)
        
        # Plot Hydrogen Bond Distribution
        fig_dist = plot_distribution(all_y_data, labels, st.session_state.customizations_dist)
        st.pyplot(fig_dist)
        link_dist = get_download_link(fig_dist, 'Hydrogen_Bond_Distribution')
        if link_dist:
            st.markdown(link_dist, unsafe_allow_html=True)

if __name__ == "__main__":
    hbond()

