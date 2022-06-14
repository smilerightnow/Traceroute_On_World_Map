import matplotlib.pyplot as plt
import requests, subprocess, re
import math, random, os
from adjustText import adjust_text

# pip install adjustText requests matplotlib

def degreesToRadians(degrees):
	return (degrees * math.pi) / 180

def latLonToOffsets(latitude, longitude, mapWidth, mapHeight):
	radius = mapWidth / (2 * math.pi)

	lonRad = degreesToRadians(longitude + 180)
	x = lonRad * radius

	latRad = degreesToRadians(latitude)
	verticalOffsetFromEquator = radius * math.log(math.tan(math.pi / 4 + latRad / 2))
	y = mapHeight / 2 - verticalOffsetFromEquator

	return x, y

def get_routes(of):
	if os.name == "nt": ## if windows
		out = subprocess.check_output(['tracert', of]).decode('utf-8')
	else: ##if linux/mac
		out = subprocess.check_output(['traceroute', of]).decode('utf-8')
	ips_with_order = {}
	ips = []
	lines = out.split("\n")

	for line in lines:
		try:
			ip = re.findall(r"(\d*\.\d*\.\d*\.\d*)", line)[0]
			number = re.findall(r"^ *(\d+) ", line)[0]

			if not ip.startswith("10.") and not ip.startswith("192.168."):
				if ip.startswith("172."):
					byte = int(ip.split(".")[1])
					if not byte >= 16 and not byte < 32:
						ips_with_order[number] = ip
						ips.append(ip)
				else:
					ips_with_order[number] = ip
					ips.append(ip)
		except:
			pass
	
	routes = []
	headers = {
		'Content-Type': 'application/json',
	}
		
	r = requests.post('http://ipinfo.io/batch?token=e429dec447446f', headers=headers, json=ips).json()

	for order, ip in ips_with_order.items():
		if ip in r:
			data = r[ip]
			if "loc" in data:
				city, lat, lon = data["city"] + ", " + data["country"], data["loc"].split(",")[0], data["loc"].split(",")[1]
				x, y = latLonToOffsets(float(lat), float(lon), 2048, 1588)
				
				routes.append([x, y, city])
			
	new_routes = []
	for r in routes:
		if not r in new_routes:
			print(r[2])
			new_routes.append(r)
		
	return new_routes

def plot_lines(points):
	dpi = 80
	im_data = plt.imread("map.jpg")
	height, width, depth = im_data.shape

	figsize = width / float(dpi), height / float(dpi)

	plt.figure(figsize=figsize)

	plt.axis('off')

	plt.imshow(im_data)

	xs = [p[0] for p in points]
	ys = [p[1] for p in points]
	cities = [p[2] for p in points]
	
	plt.plot(xs, ys, linewidth = 3, zorder=1)

	plt.scatter(xs, ys, c="red", zorder=2)
	
	texts = []

	for i, txt in enumerate(cities):
		if not txt in texts:
			texts.append(plt.text(xs[i], ys[i], txt, color="white",
				bbox=dict(boxstyle='round,pad=0.2', fc='black')))
	
	adjust_text(texts, expand_points=(1.5,1.5), expand_text=(1.5,1.5), arrowprops=dict(lw=2 , arrowstyle='->', connectionstyle='arc3,rad=0.5', color='red'))
			
	plt.savefig("result.png", bbox_inches='tight')


points = get_routes("yahoo.com")

plot_lines(points)
