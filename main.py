from Camera import *
from InverseCamera import *
import matplotlib.pyplot as plt
import sys
from PIL import Image, ExifTags


def sum_sq_error(arg1, arg2):

    return np.sum(np.square(arg1 - arg2))


def plot_gcp(uv, img):

    u, v = uv[:, 0], uv[:, 1]

    # Plot the uv ground control points
    plt.figure(figsize=(10, 13))
    plt.imshow(img)
    plt.scatter(u, v, color='r')
    plt.show()


def plot_fit(uv, puv, img):

    u, v = uv[:, 0], uv[:, 1]
    pu, pv = puv[0], puv[1]

    plt.figure(figsize=(15, 15))
    plt.imshow(img)
    plt.scatter(u, v, color='r', s=50, label="GCP")
    plt.scatter(pu, pv, color='c', s=50, label="Estimate")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()


def parse_args(argv):

    img_files = []
    gcp_files = []

    for i in range(0, len(argv), 2):
        img_files.append(argv[i])
        gcp_files.append(argv[i + 1])

    return img_files, gcp_files


def make_p0(ene):

    # Use one of the points as a basis for the initial guess
    ene0 = ene[:, 0].tolist()
    # Shift back to make sure all points are on the sensor
    ene0[0] -= 1000

    p0 = ene0

    # Assume looking straight East
    p0.extend([90, 0, 0])

    return p0


def read_gcp_nh(gcp_fname):

    uv_ene = np.loadtxt(gcp_fname, delimiter=',')
    uv, ene = uv_ene[:, 0:2], uv_ene[:, 2:]

    return uv, ene


def get_calibrated_cameras(img_files, gcp_files, f_length, sensor_size, check_calibration=False):

    cam_list = []
    for img_fname, gcp_fname in zip(img_files, gcp_files):

        # Setup camera model.
        # Presumably, this is the same
        # for all pictures.
        cam = Camera(f_length, sensor_size)

        # Read in image and ground control points
        img = plt.imread(img_fname)
        uv, ene = read_gcp_nh(gcp_fname)

        # Make initial pose guess
        p0 = make_p0(ene.T)

        # Estimate pose
        cam.estimate_pose(ene.T, uv.T, p0)
        print("Estimated pose:", cam.p.tolist())

        cam_list.append(cam)

        if check_calibration:

            # Visually test the fit
            puv = cam.ene_to_camera(ene.T)
            plot_fit(uv, puv, img)

            print("SSE:", sum_sq_error(uv, puv.T), '\n')

    return cam_list


def main(argv):

    if len(argv) % 2 != 0:
        print("usage: estimate_pose: <img1> <gcp1> [img2] [gcp[2]...")
        sys.exit(1)

    # Get relevant exif data
    img = Image.open(argv[0])
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}

    img_width = int(exif['ImageWidth'])
    img_height = int(exif['ImageLength'])
    f_length_35 = int(exif['FocalLengthIn35mmFilm'])

    f_length = f_length_35 / 36 * img_width
    sensor_size = (img_width, img_height)

    print("focal length:", f_length)
    print("sensor size:", sensor_size, '\n')

    img_files, gcp_files = parse_args(argv)
    cam_list = get_calibrated_cameras(img_files, gcp_files, f_length, sensor_size)

    # Read in clock tower GCP
    uv, ene = read_gcp_nh('main_hall_clock.txt')

    i_cam = InverseCamera()

    X0 = np.zeros((3))

    # Use the average position of the cameras to compute initial guess
    for cam in cam_list:
        X0 += cam.p[:3]

    X0 /= len(cam_list)

    i_cam.estimate_points(cam_list, uv.T, X0)

    print('\nEstimated ene:', i_cam.x_pt)
    print('Actual ene:', ene[0])
    print('\nabs difference:', np.abs(i_cam.x_pt - ene[0]))
    print('sse:', sum_sq_error(i_cam.x_pt, ene[0]))


if __name__ == '__main__':
    main(sys.argv[1:])
