import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, Optional

from src.discovery_sheet import format_markdown


def export_discovery_sheet(discovery_sheet: Dict[str, Any], output_path: str, format_type: str, config: Dict[str, Any]) -> str:
    """Export the discovery sheet to the specified format.
    
    Args:
        discovery_sheet: Discovery sheet data
        output_path: Path to save the output file
        format_type: Output format (markdown, csv, json, pdf)
        config: Application configuration
        
    Returns:
        Path to the exported file
    """
    # Add timestamp to metadata
    discovery_sheet['metadata']['analysis_timestamp'] = datetime.now().isoformat()
    
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Export based on format type
    if format_type == 'markdown':
        return export_markdown(discovery_sheet, output_path)
    elif format_type == 'csv':
        return export_csv(discovery_sheet, output_path)
    elif format_type == 'json':
        return export_json(discovery_sheet, output_path)
    elif format_type == 'pdf':
        return export_pdf(discovery_sheet, output_path, config)
    else:
        raise ValueError(f"Unsupported export format: {format_type}")


def export_markdown(discovery_sheet: Dict[str, Any], output_path: str) -> str:
    """Export the discovery sheet as a Markdown file.
    
    Args:
        discovery_sheet: Discovery sheet data
        output_path: Path to save the output file
        
    Returns:
        Path to the exported file
    """
    markdown_content = format_markdown(discovery_sheet)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_path


def export_csv(discovery_sheet: Dict[str, Any], output_path: str) -> str:
    """Export the discovery sheet as a CSV file.
    
    Args:
        discovery_sheet: Discovery sheet data
        output_path: Path to save the output file
        
    Returns:
        Path to the exported file
    """
    content = discovery_sheet.get('content', {})
    
    # Flatten the nested structure
    flat_data = {}
    for section_title, section_data in content.items():
        for field_name, field_value in section_data.items():
            column_name = f"{section_title} - {field_name}"
            flat_data[column_name] = field_value if field_value else ""
    
    # Add metadata
    for key, value in discovery_sheet.get('metadata', {}).items():
        flat_data[f"Metadata - {key}"] = value
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(flat_data.keys())
        
        # Write values
        writer.writerow(flat_data.values())
    
    return output_path


def export_json(discovery_sheet: Dict[str, Any], output_path: str) -> str:
    """Export the discovery sheet as a JSON file.
    
    Args:
        discovery_sheet: Discovery sheet data
        output_path: Path to save the output file
        
    Returns:
        Path to the exported file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(discovery_sheet, f, indent=2, ensure_ascii=False)
    
    return output_path


def export_pdf(discovery_sheet: Dict[str, Any], output_path: str, config: Dict[str, Any]) -> str:
    """Export the discovery sheet as a PDF file.
    
    Args:
        discovery_sheet: Discovery sheet data
        output_path: Path to save the output file
        config: Application configuration
        
    Returns:
        Path to the exported file
    """
    try:
        # First convert to markdown
        markdown_content = format_markdown(discovery_sheet)
        
        # Try to import weasyprint
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            raise ImportError("PDF export requires the weasyprint package. Please install it with 'pip install weasyprint'.")
        
        # Get template path from config
        templates_dir = config.get('export', {}).get('templates_dir', './templates')
        css_path = os.path.join(templates_dir, 'pdf_style.css')
        
        # Default CSS if template doesn't exist
        default_css = """
        @page {
            margin: 1cm;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5em;
        }
        h2 {
            color: #3498db;
            margin-top: 1.5em;
        }
        h3 {
            color: #555;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 1em;
            overflow-x: auto;
        }
        """
        
        # Use CSS template if exists, otherwise use default
        css_text = default_css
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css_text = f.read()
        
        # Create temporary HTML file
        import tempfile
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, "discovery_sheet_temp.html")
        
        # Convert markdown to HTML
        try:
            import markdown
            html_content = markdown.markdown(markdown_content)
        except ImportError:
            # Simple fallback markdown to HTML conversion
            html_content = markdown_content.replace("\n\n", "</p><p>")
            html_content = f"<p>{html_content}</p>"
            html_content = html_content.replace("# ", "<h1>")
            html_content = html_content.replace("\n## ", "</p><h2>")
            html_content = html_content.replace("\n### ", "</p><h3>")
            for i in range(1, 4):
                html_content = html_content.replace(f"<h{i}>", f"</p><h{i}>")
                closing_tag_index = html_content.find("\n", html_content.find(f"<h{i}>"))
                if closing_tag_index != -1:
                    html_content = html_content[:closing_tag_index] + f"</h{i}>" + html_content[closing_tag_index:]
            html_content = html_content.replace("```\n", "<pre>")
            html_content = html_content.replace("\n```", "</pre>")
        
        # Create full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Discovery Sheet</title>
            <style>
            {css_text}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Write HTML to temp file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(filename=html_path)
        css = CSS(string=css_text, font_config=font_config)
        html.write_pdf(output_path, stylesheets=[css], font_config=font_config)
        
        # Clean up temp file
        if os.path.exists(html_path):
            os.remove(html_path)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"PDF export failed: {str(e)}")
