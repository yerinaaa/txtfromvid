# USAGE
# python main.py --filename video.png
# python main.py -f video.png -e es.belyak@gmail.com -t 600 -c 90

from localize import LocalizeText
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required = True,
                help = "path to video")
ap.add_argument("-e", "--email_to_share",
                 help = "emails for share table")
ap.add_argument("-t", "--time_next_frame", type = int, default = 10,
                help = "time in seconds for next frame")
ap.add_argument("-c", "--min_conf", type = int, default = 75,
                help = "mininum confidence value to filter weak text detection")
args = vars(ap.parse_args())

# emails = ['esbelyakova@miem.hse.ru', 'es.belyak@gmail.com']

# ocr = LocalizeText(filename = 'video_test.mp4', email_to_share = emails, time_next_frame = 300, min_conf = 85)

ocr = LocalizeText(filename = args["filename"], email_to_share = args["email_to_share"], time_next_frame = args["time_next_frame"], min_conf = args["min_conf"])

ocr.run()