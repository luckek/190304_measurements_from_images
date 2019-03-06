from Camera import *
import matplotlib.pyplot as plt

img_width = int(3264)
img_height = int(2448)
f_length_35 = int(27)

f_length = f_length_35/36*img_width
print(f_length)

sensor_size = (img_width, img_height)

img_1 = plt.imread("campus_stereo_1.jpg")
img_2 = plt.imread("campus_stereo_2.jpg")

uv_ene = np.loadtxt("gcp_stereo_1.txt", delimiter=',')

uv, ene = uv_ene[:, 0:2], uv_ene[:, 2:]

uv = np.asarray(uv, dtype=int)
u, v = uv[:, 0], uv[:, 1]

# Plot the uv ground control points
plt.figure(figsize=(10, 13))
plt.imshow(img_1)
plt.scatter(u, v, color='r')
plt.show()

cam = Camera()
cam.f = f_length
cam.sensor_size = sensor_size

ene_t = ene.T

# Use one of the points as a basis for the initial guess
ene0 = ene_t[:, 0].tolist()
# Shift back to make sure all points are on the sensor
ene0[0] -= 1000

p0 = ene0
# Assume looking straight East
p0.extend([90, 0, 0])

cam.p0 = np.array(p0)
cam.estimate_pose(ene.T, uv.T)
print(cam.p)

# Visually test the fit
puv = cam.ene_to_camera(ene.T)
plt.figure(figsize=(15, 15))
plt.imshow(img_1)
plt.scatter(u, v, color='r', s=50, label="GCP")
plt.scatter(puv[0], puv[1], color='c', s=50, label="Estimate")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()
