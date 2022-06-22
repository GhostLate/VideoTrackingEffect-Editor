import cv2
import sys

if __name__ == '__main__':
    tracker_types = ['DaSiamRPN', 'CSRT']
    tracker_type = tracker_types[1]

    if tracker_type == 'DaSiamRPN':
        params = cv2.TrackerDaSiamRPN_Params()
        params.model = "./models/dasiamrpn/dasiamrpn_model.onnx"
        params.kernel_cls1 = "./models/dasiamrpn/dasiamrpn_kernel_cls1.onnx"
        params.kernel_r1 = "./models/dasiamrpn/dasiamrpn_kernel_r1.onnx"
        tracker = cv2.TrackerDaSiamRPN_create(params)
    else:
        tracker = cv2.TrackerCSRT_create()

    # Read video
    video = cv2.VideoCapture("../sample.mp4")

    # Exit if video not opened.
    if not video.isOpened():
      print("Could not open video")
      sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
      print ('Cannot read video file')
      sys.exit()

    # Define an initial bounding box
    #bbox = (287, 23, 86, 320)

    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False)
    print(bbox)
    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)
    print(f"{ok=}, {bbox=}")

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)
        print(f"{ok=}, {bbox=}")

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display tracker type on frame
        cv2.putText(frame, tracker_type + " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
        # Display result
        cv2.imshow("Tracking", frame)

        # Exit if ESC pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press SPACE bar
            break

    video.release()
    cv2.destroyAllWindows()