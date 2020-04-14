import io


# perpare image for html transfer
# reference: https://towardsdatascience.com/python-plotting-api-expose-your-scientific-python-plots-through-a-flask-api-31ec7555c4a8

def img_bytes(plt):
	bytes_image = io.BytesIO()
	plt.savefig(bytes_image, format='png', bbox_inches = "tight")
	bytes_image.seek(0)
	return bytes_image
