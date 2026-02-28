export function getIconUrl(file_type) {
  return `/assets/drive/images/icons/${file_type.toLowerCase()}.svg`
}

export function getThumbnailUrl({ name, file_type, thumbnail, external, is_attachment }) {
  // External presentations (e.g., Google Slides)
  if (external) return [thumbnail, getIconUrl("presentation"), false]
  
  const HTML_THUMBNAILS = ["Markdown", "Code", "Text", "Document"]
  const IMAGE_THUMBNAILS = ["Image", "Video", "PDF", "Presentation"]
  const is_image = IMAGE_THUMBNAILS.includes(file_type)
  const iconURL = getIconUrl(file_type.toLowerCase())
  
  // For Frappe attachments, use thumbnail directly if provided (e.g., image URL)
  if (is_attachment && thumbnail) {
    return [thumbnail, iconURL, true]
  }
  
  if (!is_image && !HTML_THUMBNAILS.includes(file_type))
    return [null, iconURL, true]
  
  return [
    `/api/method/drive.api.files.get_thumbnail?entity_name=${name}`,
    iconURL,
    is_image,
  ]
}
