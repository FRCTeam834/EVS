import time
import edgeiq
import pyfrc
from networktables import NetworkTables
import logging

# Constant for the default confidence (0 being 0% sure and 1 being 100% sure)
default_conf_thres = .5

'''
The idea for the organization was as follows:

\ - table
no character - variable

\VisionValues
    \Hatch0
    \Hatch1
    \Hatch2
    \Hatch3
    \Hatch4
    \Ball0
    \Ball1
    \Ball2
    \Ball3
    \Ball4
    \Tape0
    ...
    \Tape9
    
    update - boolean used to store if new values are available to the Rio.
    
    
    Each of those subtables would have these values:
    inUse
    values
    
    Definitions:
    inUse - boolean to specify if the RoboRio has to read the values for that table. Changes to 
            true when the camera has that object in it. The Rio goes down the list, checking to 
            see if that one is used and stops after it finds the first table not being used
    values - an array that will store the values. Makes it easier to call and faster than having to
             specify each one


'''

def main():

    # Setup logging for the NetworkTables messages
    logging.basicConfig(level=logging.DEBUG)

    # Setup NetworkTables
    NetworkTables.initialize(server = '10.8.34.2')

    # Create table for values
    val = NetworkTables.createTable('VisionValues')
    sd = NetworkTables.getTable('SmartDashboard')

    # Setup EdgeIQ
    obj_detect = edgeiq.ObjectDetection(
            "alwaysai/mobilenet_ssd")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    # Print out info
    print("Loaded model:\n{}\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Labels:\n{}\n".format(obj_detect.labels))

    # Get the FPS
    fps = edgeiq.FPS()

    sd.putString('DB/String 3', default_conf_thres)

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream, \
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:

                # Grab value for confidence from SmartDashboard, if it can't, use default
                confidence_thres = val.getString('DB/String 3', default_conf_thres)

                try:
                    # Try converting string to a float
                    confidence_thres = float(confidence_thres)
                except:
                    # If that fails, set the confidence threshold to the default value
                    confidence_thres = default_conf_thres

                frame = video_stream.read()
                results = obj_detect.detect_objects(frame, confidence_level = confidence_thres)
                frame = edgeiq.markup_image(
                        frame, results.predictions, colors=obj_detect.colors)

                # Update the VisionValues NetworkTable with new values
                for prediction in results.predictions:
                    # Remove these; they are irrelevant; replace them with the NetworkTables code
                    val.putString((prediction.index + '.label') , prediction.label)
                    val.putNumber((prediction.index + '.center'), prediction.center)
                    val.putNumber((prediction.index + '.endX')  , prediction.end_x)
                    val.putNumber((prediction.index + '.endY')  , prediction.end_y)
                    val.putNumber((prediction.index + '.area')  , prediction.area)
                    val.putNumber((prediction.index + '.conf')   , (prediction.confidence * 100))


                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append("Inference time: {:1.3f} s".format(results.duration))
                text.append("Objects:")

                # Format and display values on localhost streamer
                for prediction in results.predictions:
                    text.append("{}: {:2.2f}%".format(
                        prediction.label, prediction.confidence * 100))

                streamer.send_data(frame, text)

                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
