import time
import edgeiq
import pyfrc
from networktables import NetworkTables
import logging

# Constant for the default confidence (0 being 0% sure and 1 being 100% sure)
default_conf_thres = .5

# TODO: Order the predictions in terms of priority (proximity?)

def main():

    # Setup logging for the NetworkTables messages
    logging.basicConfig(level=logging.DEBUG)

    # Setup NetworkTables
    NetworkTables.initialize(server = '10.8.34.2')

    # Create table for values
    val = NetworkTables.getTable('VisionValues')
    sd = NetworkTables.getTable('SmartDashboard')

    # Create sub-tables and append them to arrays: 3 for hatches, 3 for balls, and 6 for tape
    hatchTables = []
    ballTables = []
    tapeTables = []

    hatch0 = val.getSubTable('Hatch0')
    hatchTables.append(hatch0)
    hatch1 = val.getSubTable('Hatch1')
    hatchTables.append(hatch1)
    hatch2 = val.getSubTable('Hatch2')
    hatchTables.append(hatch2)

    ball0 = val.getSubTable('Ball0')
    ballTables.append(ball0)
    ball1 = val.getSubTable('Ball1')
    ballTables.append(ball1)
    ball2 = val.getSubTable('Ball2')
    ballTables.append(ball2)
    
    tape0 = val.getSubTable('Tape0')
    tapeTables.append(tape0)
    tape1 = val.getSubTable('Tape1')
    tapeTables.append(tape1)
    tape2 = val.getSubTable('Tape2')
    tapeTables.append(tape2)
    tape3 = val.getSubTable('Tape3')
    tapeTables.append(tape3)
    tape4 = val.getSubTable('Tape4')
    tapeTables.append(tape4)
    tape5 = val.getSubTable('Tape5')
    tapeTables.append(tape5)

        # Setup EdgeIQ
    obj_detect = edgeiq.ObjectDetection(
            "alwaysai/mobilenet_ssd")
    obj_detect.load(engine=edgeiq.Engine.DNN_OPENVINO)

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

            for i in range(0,2):
                hatchTables[i].putBoolean('inUse', False)
                ballTables[i].putBoolean('inUse', False)
                tapeTables[i].putBoolean('inUse', False)
                tapeTables[i+3].putBoolean('inUse', False)

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

                #Counters - they reset after every frame in the while loop
                hatchCounter = 0
                ballCounter = 0
                tapeCounter = 0
                                        
                # Update the VisionValues NetworkTable with new values
                for prediction in results.predictions:                                                                                                                        

                    # Code goes here
                    numValues = [prediction.box.center, prediction.box.end_x, prediction.box.end_y, prediction.box.area, (prediction.confidence*100)]
                    
                    #
                    # IMPORTANT:
                    # Names of labels have not been decided yet
                    #
                    #
                    if prediction.label == "Hatch":
                        # Do label separately because it is a string
                        hatchTables[hatchCounter].putString('label', prediction.label)

                        hatchTables[hatchCounter].putNumberArray('values', numValues)
                        # Boolean asks to update
                        hatchTables[hatchCounter].putBoolean('inUse', True)

                        hatchCounter += 1

                    if prediction.label == "Ball":
                        # Do label separately because it is a string
                        ballTables[ballCounter].putString('label', prediction.label)

                        ballTables[ballCounter].putNumberArray('values', numValues)
                        # Boolean asks to update
                        ballTables[ballCounter].putBoolean('inUse', True)

                        ballCounter += 1

                    if prediction.label == "Tape":
                        # Do label separately because it is a string
                        tapeTables[tapeCounter].putString('label', prediction.label)

                        tapeTables[tapeCounter].putNumberArray('values', numValues)
                        # Boolean asks to update
                        tapeTables[tapeCounter].putBoolean('inUse', True)

                        tapeCounter += 1                      

                # Sets the value after the last value to false. The Rio will stop when it finds a False
                hatchTables[hatchCounter].putBoolean('inUse', False)
                ballTables[ballCounter].putBoolean('inUse', False)
                tapeTables[tapeCounter].putBoolean('inUse', False)

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
