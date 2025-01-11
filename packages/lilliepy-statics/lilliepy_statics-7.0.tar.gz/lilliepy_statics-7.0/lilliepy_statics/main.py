from reactpy import component, html
from pathlib import Path
import base64
import inspect

_pathway = None

def static(path_to_static_content):
    """
    Set the static directory path relative to the file that called this function.
    """
    global _pathway
    
    caller_frame = inspect.stack()[1]
    caller_file = Path(caller_frame.filename).resolve()
    
    caller_folder = caller_file.parent
    path = (caller_folder / path_to_static_content).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Static content path {path} does not exist.")
    
    _pathway = path


@component
def use_CSS(css_file):
    """
    ReactPy component to load CSS content into a <style> tag.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    css_path = _pathway / css_file
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file {css_path} does not exist.")
    
    with open(css_path, 'r') as file:
        css_content = file.read()
    
    return html.style(css_content)

@component
def use_JS(js_file, module=False):
    """
    ReactPy component to load JS content into a <script> tag.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    js_path = _pathway / js_file
    if not js_path.exists():
        raise FileNotFoundError(f"JS file {js_path} does not exist.")
    
    with open(js_path, 'r') as file:
        js_content = file.read()
    
    script_attrs = {"type": "module"} if module else {}
    
    return html.script(script_attrs, js_content)

@component
def use_PY(py_file):
    """
    ReactPy component to load pyscript content into a <script type="mpy"> tag.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    py_path = _pathway / py_file
    if not py_path.exists():
        raise FileNotFoundError(f"JS file {py_path} does not exist.")
    
    with open(py_path, 'r') as file:
        py_content = file.read()

    @component
    def pyscript(content):
        return f"<pyscript>\n {content} \n</pyscript>"
    
    return html._(
        html.link({"rel": "stylesheet", "href": "https://pyscript.net/releases/2023.11.2/core.css"}),
        html.script({"type": "module", "src": "https://pyscript.net/releases/2023.11.2/core.js"}),
        pyscript(py_content)
    )

@component
def link_CSS(css_file):
    """
    ReactPy component to link CSS content as a Base64-encoded data URI.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")

    css_path = _pathway / css_file
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file {css_path} does not exist.")

    with open(css_path, "r", encoding="utf-8") as file:
        css_content = file.read()

    
    base64_css = base64.b64encode(css_content.encode("utf-8")).decode("utf-8")
    data_uri = f"data:text/css;base64,{base64_css}"

    
    return html.link({"rel": "stylesheet", "href": data_uri})


@component
def link_JS(js_file, module=False):
    """
    ReactPy component to link JavaScript content as a Base64-encoded data URI.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")

    js_path = _pathway / js_file
    if not js_path.exists():
        raise FileNotFoundError(f"JavaScript file {js_path} does not exist.")

    with open(js_path, "r", encoding="utf-8") as file:
        js_content = file.read()

    
    base64_js = base64.b64encode(js_content.encode("utf-8")).decode("utf-8")
    data_uri = f"data:application/javascript;base64,{base64_js}"

    script_attrs = {"src": data_uri}
    if module:
        script_attrs["type"] = "module"

    
    return html.script(script_attrs)


@component
def link_PY(py_file):
    """
    ReactPy component to link Python content as a Base64-encoded data URI for PyScript.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")

    py_path = _pathway / py_file
    if not py_path.exists():
        raise FileNotFoundError(f"Python file {py_path} does not exist.")

    with open(py_path, "r", encoding="utf-8") as file:
        py_content = file.read()

    
    base64_py = base64.b64encode(py_content.encode("utf-8")).decode("utf-8")
    data_uri = f"data:application/python;base64,{base64_py}"

    return html._(
        html.link({"rel": "stylesheet", "href": "https://pyscript.net/releases/2023.11.2/core.css"}),
        html.script({"type": "module", "src": "https://pyscript.net/releases/2023.11.2/core.js"}),
        html.script({"type": "text/python", "src": data_uri}),
    )

@component
def use_Image(media_file, alt_text="", return_src=False, other_attrs = None):
    """
    ReactPy component to handle image media files and embed them as Base64 data URIs.
    
    Parameters:
        media_file (str): The name of the image file.
        alt_text (str): Alt text for the image file.
        return_src (bool): if true, it will return the src of the image only
        other_attrs (dict): other attributes for the image element
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    media_path = _pathway / media_file
    if not media_path.exists():
        raise FileNotFoundError(f"Media file {media_path} does not exist.")
    
    
    file_extension = media_path.suffix.lower()
    if file_extension in [".png"]:
        mime_type = "image/png"
    elif file_extension in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif file_extension in [".gif"]:
        mime_type = "image/gif"
    else:
        raise ValueError(f"Unsupported image file type: {file_extension}")
    
    
    with open(media_path, "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    
    
    data_uri = f"data:{mime_type};base64,{base64_image}"
    
    attrs = {"src": data_uri, "alt": alt_text}
    if other_attrs:
        attrs.update(other_attrs)
    
    if return_src:
        return html.img(attrs).get("attributes").get("src")
    else:
        return html.img(attrs)

@component
def use_Video(media_file, return_src=False, other_attrs=None):
    """
    ReactPy component to handle video media files and embed them as Base64 data URIs.
    
    Parameters:
        media_file (str): The name of the video file.
        return_src (bool): If true, returns the `src` of the video only.
        other_attrs (dict): Other attributes for the video element.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    media_path = _pathway / media_file
    if not media_path.exists():
        raise FileNotFoundError(f"Media file {media_path} does not exist.")
    
    
    file_extension = media_path.suffix.lower()
    if file_extension in [".mp4"]:
        mime_type = "video/mp4"
    elif file_extension in [".webm"]:
        mime_type = "video/webm"
    elif file_extension in [".ogg"]:
        mime_type = "video/ogg"
    else:
        raise ValueError(f"Unsupported video file type: {file_extension}")
    
    
    with open(media_path, "rb") as file:
        video_data = file.read()
    base64_video = base64.b64encode(video_data).decode("utf-8")
    
    
    data_uri = f"data:{mime_type};base64,{base64_video}"
    
    
    attrs = {"src": data_uri, "controls": True}  
    if other_attrs:
        attrs.update(other_attrs)
    
    if return_src:
        return attrs["src"]
    else:
        return html.video(attrs)

@component
def use_File(media_file, return_src=False, display_as_text=False, other_attrs=None):
    """
    ReactPy component to handle generic files, including 3D file formats, and embed them as Base64 data URIs.
    
    Parameters:
        media_file (str): The name of the file.
        return_src (bool): If true, returns the Base64 `src` of the file only.
        display_as_text (bool): If true, displays the file content as text if supported (e.g., `.txt`, `.csv`).
        other_attrs (dict): Other attributes for the element.
    """
    global _pathway
    if _pathway is None:
        raise ValueError("Static path is not set. Call static() first.")
    
    media_path = _pathway / media_file
    if not media_path.exists():
        raise FileNotFoundError(f"Media file {media_path} does not exist.")
    
    
    file_extension = media_path.suffix.lower()
    mime_types = {
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".json": "application/json",
        ".obj": "model/obj",
        ".stl": "model/stl",
        ".gltf": "model/gltf+json",
        ".glb": "model/gltf-binary",
    }
    mime_type = mime_types.get(file_extension, "application/octet-stream")
    
    
    with open(media_path, "rb") as file:
        file_data = file.read()
    base64_file = base64.b64encode(file_data).decode("utf-8")
    
    
    data_uri = f"data:{mime_type};base64,{base64_file}"
    
    if return_src:
        return data_uri
    
    
    if display_as_text and mime_type.startswith("text/"):
        try:
            file_content = file_data.decode("utf-8")
            return html.pre({"style": {"whiteSpace": "pre-wrap"}}, file_content)
        except UnicodeDecodeError:
            raise ValueError(f"Cannot display {media_file} as text.")
    
    
    attrs = {"href": data_uri, "download": media_file.name}
    if other_attrs:
        attrs.update(other_attrs)
    
    return html.a(attrs, f"Download {media_file}")