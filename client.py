def upload_to_signed_url(self, url: str, data: bytes, headers: Dict[str, str]) -> None:
    """Low-level API call to upload file data to a signed URL"""
    response = requests.put(url, data=data, headers=headers)
    response.raise_for_status()
    # PUT requests to signed URLs typically return no content
    return None 