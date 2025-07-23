"""
Main application entry point for MCP Client Console.
"""

import asyncio

import streamlit as st

from ..core.client import MCPClientService
from ..core.models import ConnectionConfig
from ..utils.error_handler import ErrorHandler
from ..utils.logger import configure_logging

# Configure logging
configure_logging(level="INFO")


def display_error(error: Exception, context: str = ""):
    """Display error in the UI."""
    friendly_message = ErrorHandler.get_user_friendly_message(error)
    st.error(f"❌ {friendly_message}")

    with st.expander("Detailed Error Information"):
        error_details = ErrorHandler.format_error_details(error)
        st.json(error_details)


def create_tool_form(tool_info, tool_index: int):
    """Create a form for tool execution."""
    if not tool_info.input_schema:
        st.info("This tool has no parameters")
        return {}, True

    with st.form(key=f"tool_form_{tool_info.name}_{tool_index}"):
        st.write("**Execute Tool:**")
        args = {}

        # Parse schema to create form inputs
        schema = tool_info.input_schema
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}

        if properties:
            for arg_name, arg_info in properties.items():
                arg_type = arg_info.get("type", "string")
                default_val = arg_info.get("default")
                description = arg_info.get("description", "")

                # Display argument description if available
                if description:
                    st.write(f"*{arg_name}*: {description}")

                # Create input field based on type
                if arg_type == "number" or arg_type == "integer":
                    default = float(default_val) if default_val is not None else 0.0
                    if arg_type == "integer":
                        args[arg_name] = st.number_input(
                            f"{arg_name}",
                            value=int(default),
                            step=1,
                            key=f"{tool_info.name}_{arg_name}_{tool_index}",
                        )
                    else:
                        args[arg_name] = st.number_input(
                            f"{arg_name}",
                            value=default,
                            key=f"{tool_info.name}_{arg_name}_{tool_index}",
                        )
                elif arg_type == "boolean":
                    default = bool(default_val) if default_val is not None else False
                    args[arg_name] = st.checkbox(
                        f"{arg_name}",
                        value=default,
                        key=f"{tool_info.name}_{arg_name}_{tool_index}",
                    )
                elif arg_type == "array":
                    import json

                    default = str(default_val) if default_val is not None else ""
                    json_input = st.text_area(
                        f"{arg_name} (JSON array)",
                        value=default,
                        help="Enter a JSON array",
                        key=f"{tool_info.name}_{arg_name}_{tool_index}",
                    )
                    # Try to parse as JSON
                    try:
                        args[arg_name] = json.loads(json_input) if json_input else []
                    except json.JSONDecodeError:
                        st.error(f"Invalid JSON for {arg_name}")
                        args[arg_name] = []
                else:  # string or other
                    default = str(default_val) if default_val is not None else ""
                    args[arg_name] = st.text_input(
                        f"{arg_name}",
                        value=default,
                        key=f"{tool_info.name}_{arg_name}_{tool_index}",
                    )

        submitted = st.form_submit_button("Execute Tool")
        return args, submitted


def main():
    st.set_page_config(
        page_title="MCP Client Test Console", page_icon="🔧", layout="wide"
    )

    st.title("🔧 MCP Client Test Console")
    st.markdown("A testing tool for MCP (Model Context Protocol) server compliance")

    # Initialize session state
    if "mcp_service" not in st.session_state:
        st.session_state.mcp_service = MCPClientService()
    if "connected" not in st.session_state:
        st.session_state.connected = False

    # Sidebar for connection settings
    with st.sidebar:
        st.header("Connection Settings")

        connection_type = st.selectbox(
            "Connection Type:", ["stdio", "sse", "http"], key="connection_type"
        )

        # Connection parameters based on type
        if connection_type == "stdio":
            st.subheader("STDIO Configuration")
            command = st.text_input("Command:", value="python", key="stdio_command")
            args_text = st.text_input("Arguments (space-separated):", key="stdio_args")
            args = args_text.split() if args_text else []

            connection_params = {"command": command, "args": args}

        elif connection_type == "sse":
            st.subheader("SSE Configuration")
            url = st.text_input(
                "SSE URL:", value="http://localhost:8000/sse", key="sse_url"
            )

            connection_params = {"url": url}

        elif connection_type == "http":
            st.subheader("HTTP Configuration")
            base_url = st.text_input(
                "Base URL:", value="http://localhost:8000", key="http_url"
            )

            connection_params = {"base_url": base_url}

        # Connect button
        if st.button("Connect"):
            connection_config = ConnectionConfig(
                connection_type=connection_type, parameters=connection_params
            )

            with st.spinner("Connecting..."):
                try:
                    server_info = asyncio.run(
                        st.session_state.mcp_service.connect(connection_config)
                    )
                    st.session_state.connected = True
                    st.success("Connected successfully!")
                except Exception as e:
                    st.session_state.connected = False
                    display_error(e, "connection")

        # Disconnect button
        if st.session_state.connected:
            if st.button("Disconnect", type="secondary"):
                try:
                    asyncio.run(st.session_state.mcp_service.disconnect())
                    st.session_state.connected = False
                    st.success("Disconnected!")
                except Exception as e:
                    display_error(e, "disconnection")

    # Main content area
    if st.session_state.connected:
        service = st.session_state.mcp_service

        # Server Information
        st.header("📋 Server Information")
        server_info = service.get_server_info()
        if server_info and server_info.raw_data:
            st.json(server_info.raw_data)
        else:
            st.info("No server information available")

        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["🛠️ Tools", "💬 Prompts", "📄 Resources"])

        with tab1:
            st.subheader("Available Tools")
            tools = service.get_tools()

            if tools:
                for i, tool in enumerate(tools):
                    with st.expander(f"🛠️ {tool.name}"):
                        st.write(f"**Description:** {tool.description}")

                        # Display input schema
                        if tool.input_schema:
                            st.write("**Input Schema:**")
                            st.json(tool.input_schema)

                            # Tool execution form
                            args, submitted = create_tool_form(tool, i)

                            if submitted:
                                with st.spinner("Executing tool..."):
                                    try:
                                        result = asyncio.run(
                                            service.execute_tool(tool.name, args)
                                        )

                                        if result.success:
                                            st.success("✅ Tool executed successfully!")
                                            st.write(
                                                f"**Execution time:** {result.execution_time:.2f}s"
                                            )

                                            # Display results
                                            if result.result:
                                                st.write("**Result:**")
                                                if (
                                                    hasattr(result.result, "content")
                                                    and result.result.content
                                                ):
                                                    for (
                                                        content_item
                                                    ) in result.result.content:
                                                        if hasattr(
                                                            content_item, "type"
                                                        ):
                                                            if (
                                                                content_item.type
                                                                == "text"
                                                            ):
                                                                st.text(
                                                                    content_item.text
                                                                )
                                                            elif (
                                                                content_item.type
                                                                == "image"
                                                            ):
                                                                st.image(
                                                                    content_item.data
                                                                )
                                                            else:
                                                                st.json(
                                                                    content_item.dict()
                                                                    if hasattr(
                                                                        content_item,
                                                                        "dict",
                                                                    )
                                                                    else str(
                                                                        content_item
                                                                    )
                                                                )
                                                        else:
                                                            st.write(str(content_item))
                                                else:
                                                    st.json(
                                                        result.result.dict()
                                                        if hasattr(
                                                            result.result, "dict"
                                                        )
                                                        else str(result.result)
                                                    )
                                        else:
                                            st.warning(
                                                "⚠️ Tool executed but returned no result"
                                            )

                                    except Exception as e:
                                        display_error(e, "tool execution")
                        else:
                            st.info("This tool has no input schema defined")
            else:
                st.info("No tools available")

        with tab2:
            st.subheader("Available Prompts")
            prompts = service.get_prompts()

            if prompts:
                for prompt in prompts:
                    with st.expander(f"💬 {prompt.name}"):
                        st.write(f"**Description:** {prompt.description}")
                        if prompt.arguments:
                            st.write("**Arguments:**")
                            st.json(prompt.arguments)
            else:
                st.info("No prompts available")

        with tab3:
            st.subheader("Available Resources")
            resources = service.get_resources()

            if resources:
                for resource in resources:
                    with st.expander(f"📄 {resource.uri}"):
                        if resource.name:
                            st.write(f"**Name:** {resource.name}")
                        if resource.description:
                            st.write(f"**Description:** {resource.description}")
                        if resource.mime_type:
                            st.write(f"**MIME Type:** {resource.mime_type}")
            else:
                st.info("No resources available")

    else:
        st.info("👈 Please connect to an MCP server using the sidebar")

        # Help section
        st.header("📖 How to Use")
        st.markdown(
            """
        1. **Choose a connection type** from the sidebar:
           - **STDIO**: Connect to a local MCP server process
           - **SSE**: Connect via Server-Sent Events
           - **HTTP**: Connect via HTTP transport
        
        2. **Configure the connection** parameters based on your server setup
        
        3. **Click Connect** to establish the connection
        
        4. **Explore** the server's tools, prompts, and resources once connected
        
        ### Example STDIO Configuration:
        - Command: `python`
        - Arguments: `your_mcp_server.py`
        
        ### Example SSE Configuration:
        - URL: `http://localhost:8000/sse`
        
        ### Example HTTP Configuration:
        - Base URL: `http://localhost:8000`
        """
        )


if __name__ == "__main__":
    main()
