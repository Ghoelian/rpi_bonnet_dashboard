from PIL import Image, ImageDraw, ImageFont
import inspect
import time
import speedtest
import math
import sys
from datetime import datetime
sys.path.insert(1, "./lib")

import epd2in7b

speedtest_queue = []
speedtest_delay = 60.0 * 10.0

def draw_nubers_n_hexes(down_speed, up_speed, ping, canvas, font):
    writeLog(f"Begin drawing numbers")

    scale = 2.7

    start_base = [height/2.0+30, 30]
    center = [start_base[0], start_base[1]]
    radius = [20.0*scale, 10.0*scale]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    canvas.text(get_text_start_for_hex(center, radius), down_speed, font=font, fill=0)
    center = [start_base[0], start_base[1]+radius[1]*math.sqrt(3)]
    radius = [20.0*scale, 10.0*scale]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    canvas.text(get_text_start_for_hex(center, radius), up_speed, font=font, fill=0)
    center = [start_base[0]+radius[0] + (5*scale), start_base[1]+radius[1]*math.sqrt(3)/2]
    radius = [10.0*scale, 10.0*scale]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    canvas.text(get_text_start_for_hex(center, radius), ping, font=font, fill=0)
    center = [start_base[0]+(20*scale)+(5*scale), start_base[1]+radius[1]*math.sqrt(3)/2*3]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    center = [start_base[0]+(20*scale)+(5*scale), start_base[1]+radius[1]*math.sqrt(3)/2*5]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    center = [start_base[0]-(5*scale), start_base[1]+radius[1]*math.sqrt(3)/2*5]
    canvas.polygon(generate_hexagon(center, radius), outline=0)
    writeLog(f"D:{down_speed} U:{up_speed} P:{ping}")

    down = open("./live_results/down", "w+")
    up = open("./live_results/up", "w+")
    ping = open("./live_results/ping", "w+")

    down.write(f"{down_speed}")
    up.write(f"{up_speed}")
    ping.write(f"{ping}")

    down.close()
    up.close()
    ping.close()

def network_speed_test():
    writeLog(f"Begin network speed test")
    servers = []

    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download()
    s.upload(pre_allocate=False)
    speedtest_queue.append(s)

    writeLog(f"Finish network speed test")

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def generate_hexagon(center_point, size):
    y_offset = math.sqrt(3)/2*size[1]
    x_offset = 1/2*size[1]+size[0]-size[1]
    return [
        (center_point[0] - size[0], center_point[1]),
        (center_point[0] - x_offset, center_point[1] + y_offset),
        (center_point[0] + x_offset, center_point[1] + y_offset),
        (center_point[0] + size[0], center_point[1]),
        (center_point[0] + x_offset, center_point[1] - y_offset),
        (center_point[0] - x_offset, center_point[1] - y_offset),
    ]


def get_text_start_for_hex(center, radius):
    return [center[0]-radius[0]+radius[1]/2.0, center[1]-math.sqrt(3)/4*radius[1]]


def draw_network_graph(xy, hw, canvas, canvasRed):
    writeLog(f"Begin drawing network graph")

    # Draw left bracket
    canvas.line([(xy[0] + 0, xy[1] + 0), (xy[0] + 5, xy[1] + 0)], width=1, fill=0)
    canvas.line([(xy[0] + 0, xy[1] + 0), (xy[0] + 0, xy[1] + hw[0])], width=1, fill=0)
    canvas.line([(xy[0] + 0, xy[1] + hw[0]), (xy[0] + 5, xy[1] + hw[0])], width=1, fill=0)

    # Draw right bracket
    canvas.line([(xy[0] + hw[1], xy[1] + 0), (xy[0] + hw[1] - 5, xy[1] + 0)], width=1, fill=0)
    canvas.line([(xy[0] + hw[1], xy[1] + 0), (xy[0] + hw[1], xy[1] + hw[0])], width=1, fill=0)
    canvas.line([(xy[0] + hw[1], xy[1] + hw[0]), (xy[0] + hw[1] - 5, xy[1] + hw[0])], width=1, fill=0)

    # Get auto scale max
    scale_max = sys.float_info.epsilon

    for measurement in speedtest_queue:
      if (measurement.results.upload > scale_max):
        scale_max = measurement.results.upload

      if (measurement.results.download > scale_max):
        scale_max = measurement.results.download

    queue_draw_loc_x = 6

    writeLog(f"Drawing current queue to graph")
    for measurement in speedtest_queue:
        if (queue_draw_loc_x > xy[0] + hw[1] - 1):
          writeLog("Graph full, popping first result")
          queue_draw_loc_x = 6
          speedtest_queue.pop(0)

        if measurement.results.download > 0.0:
            canvas.point([queue_draw_loc_x, translate(measurement.results.download, 0.1, scale_max, width-10, 10)], fill=0)
            canvas.point([queue_draw_loc_x+1, translate(measurement.results.download, 0.1, scale_max, width-10, 10)], fill=0)
            canvas.point([queue_draw_loc_x+1, translate(measurement.results.download, 0.1, scale_max, width-10, 10)+1], fill=0)
            canvas.point([queue_draw_loc_x, translate(measurement.results.download, 0.1, scale_max, width-10, 10)+1], fill=0)

        if measurement.results.upload > 0.0:
            canvasRed.point([queue_draw_loc_x, translate(measurement.results.upload, 0.1, scale_max, width-10, 10)], fill=0)
            canvasRed.point([queue_draw_loc_x+1, translate(measurement.results.upload, 0.1, scale_max, width-10, 10)], fill=0)
            canvasRed.point([queue_draw_loc_x+1, translate(measurement.results.upload, 0.1, scale_max, width-10, 10)+1], fill=0)
            canvasRed.point([queue_draw_loc_x, translate(measurement.results.upload, 0.1, scale_max, width-10, 10)+1], fill=0)

        if (queue_draw_loc_x <= xy[0] + hw[1] - 1):
          queue_draw_loc_x += 2

def writeLog(text):
  log = open("./log/log.txt", "a+")
  log.write(f"{datetime.now()} - {text}\r\n")
  log.close()

# Entry point of the program
if __name__ == '__main__':
    writeLog("Program start")
    writeLog(f"Speedtest delay is {speedtest_delay}")
    EXECUTION_PERIOD_S = speedtest_delay

    # Network measumenet queue
    queue_size = 95

		# Counter to determine after how many redraws it should fully clear the display
    counter = 10
    iterator = 0

    writeLog("Initialising and clearing EPD Display")
    epd = epd2in7b.EPD()
    epd.init()
    epd.Clear()

    writeLog("EPD Display cleared and ready")

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = 176
    height = 264
    image = Image.new('1', (height, width), 255)
    imageRed = Image.new('1', (height, width), 255)
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    drawRed = ImageDraw.Draw(imageRed)

    starttime = time.time() - EXECUTION_PERIOD_S

    while True:
        download_string = "----"
        upload_string = "----"
        ping_string = "--"

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, height, width), outline=1, fill=1)
        drawRed.rectangle((0, 0, height, width), outline=1, fill=1)

        if (len(speedtest_queue) >= 1):
            last_measurement_results = speedtest_queue[len(speedtest_queue)-1].results

            if last_measurement_results.download > 0.0:
                download_string = '{0:.2f}'.format(last_measurement_results.download / 1000000.0)

            if last_measurement_results.upload > 0.0:
                upload_string = '{0:.2f}'.format(last_measurement_results.upload / 1000000.0)

            if last_measurement_results.ping > 0.0:
                ping_string = '{0:.0f}'.format(last_measurement_results.ping)

        draw_nubers_n_hexes(download_string, upload_string, ping_string, draw, fnt)
        draw_network_graph([5, 5], [width - 10, queue_size - 2], draw, drawRed)
        #draw_hex_load_indicator(False, draw)

        if (iterator >= counter):
          epd.Clear()
          iterator = 0

        writeLog("Start writing new image to display")
        epd.display(epd.getbuffer(image), epd.getbuffer(imageRed))
        writeLog("Finish writing new image to display")

        iterator += 1
        time_to_sleep = EXECUTION_PERIOD_S - min((time.time() - starttime), EXECUTION_PERIOD_S)
        time.sleep(time_to_sleep)
        starttime = time.time()
        #draw_hex_load_indicator(True, draw)
        network_speed_test()

