import streamlit.components.v1 as components

_component_func = components.declare_component(
    "custom_button",
    path="frontend",
)

def custom_button(key=None):
    component_value = _component_func(key=key)
    return component_value
