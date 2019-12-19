import time
import edgeiq
import pyfrc
from networktables import NetworkTables
import logging
import numpy as np

# Constant for the default confidence (0 being 0% sure and 1 being 100% sure)
default_conf_thres = .5

def main():
    # Allow Rio to boot and configure network
    time.sleep(5.0)

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    # Setup NetworkTables
    NetworkTables.initialize(server = '10.8.34.2')

    # Create table for values
    evs = NetworkTables.getTable('EVS')
    # sd = NetworkTables.getTable('SmartDashboard')

    # Create sub-tables and append them to arrays: 3 for hatches, 3 for balls, and 6 for tape
    hatchTables = []
    ballTables = []
    tapeTables = []

    hatch0 = evs.getSubTable('Hatch0')
    hatchTables.append(hatch0)
    hatch1 = evs.getSubTable('Hatch1')
    hatchTables.append(hatch1)
    hatch2 = evs.getSubTable('Hatch2')
    hatchTables.append(hatch2)

    ball0 = evs.getSubTable('Ball0')
    ballTables.append(ball0)
    ball1 = evs.getSubTable('Ball1')
    ballTables.append(ball1)
    ball2 = evs.getSubTable('Ball2')
    ballTables.append(ball2)
    
    tape0 = evs.getSubTable('Tape0')
    tapeTables.append(tape0)
    tape1 = evs.getSubTable('Tape1')
    tapeTables.append(tape1)
    tape2 = evs.getSubTable('Tape2')
    tapeTables.append(tape2)
    tape3 = evs.getSubTable('Tape3')
    tapeTables.append(tape3)
    tape4 = evs.getSubTable('Tape4')
    tapeTables.append(tape4)
    tape5 = evs.getSubTable('Tape5')
    tapeTables.append(tape5)

    # Setup EdgeIQ
    obj_detect = edgeiq.ObjectDetection(
            "CAP1Sup/2019_FRC_GamePieces_Dev_v3")
    obj_detect.load(engine=edgeiq.Engine.DNN_OPENVINO)

    # Print out info
    print("Loaded model:\n{}\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Labels:\n{}\n".format(obj_detect.labels))

    # Get the FPS
    fps = edgeiq.FPS()
    #cross_frame_tracker = edgeiq.CorrelationTracker()
    #tracker = edgeiq.CentroidTracker()

    # sd.putString('DB/String 3', default_conf_thres)

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream:

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
                confidence_thres = default_conf_thres

                frame = video_stream.read()
                results = obj_detect.detect_objects(frame, confidence_level = confidence_thres)

                #objects = tracker.update(results.predictions)
                '''
                frame = edgeiq.markup_image(
                        frame, results.predictions, colors=obj_detect.colors)
                '''

                #Counters - they reset after every frame in the while loop
                hatchCounter = 0
                ballCounter = 0
                tapeCounter = 0

                # Update the EVS NetworkTable with new values
                for prediction in results.predictions:
 
                    center_x, center_y = prediction.box.center
                    # Code goes here
                    numValues = [center_x, center_y, prediction.box.end_x, prediction.box.end_y, prediction.box.area, (prediction.confidence * 100)]
                    
                    for entry in range(0, len(numValues) - 1):
                        numValues[entry] = round(numValues[entry], 3)

                    numValuesArray = np.asarray(numValues)
                    
                    #
                    # IMPORTANT:
                    # Names of labels have not been decided yet
                    #
                    #
                    if prediction.label == "Hatch":
                    
                        hatchTables[hatchCounter].putNumberArray('values', numValuesArray)
                        # Boolean asks to update
                        hatchTables[hatchCounter].putBoolean('inUse', True)

                        hatchCounter += 1

                    elif prediction.label == "Ball":

                        ballTables[ballCounter].putNumberArray('values', numValuesArray)
                        # Boolean asks to update
                        ballTables[ballCounter].putBoolean('inUse', True)
                        ballCounter += 1

                    elif prediction.label == "Tape":

                        tapeTables[tapeCounter].putNumberArray('values', numValuesArray)
                        # Boolean asks to update
                        tapeTables[tapeCounter].putBoolean('inUse', True)

                        tapeCounter += 1                      

                # Sets the value after the last value to false. The Rio will stop when it finds a False
                hatchTables[hatchCounter].putBoolean('inUse', False)
                ballTables[ballCounter].putBoolean('inUse', False)
                tapeTables[tapeCounter].putBoolean('inUse', False)

                evs.putBoolean('checked', False)

                
                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append("Inference time: {:1.3f} s".format(results.duration))
                text.append("Objects:")

                # Format and display values on localhost streamer
                for prediction in results.predictions:
                    text.append("{}: {:2.2f}%".format(
                        prediction.label, prediction.confidence * 100))
                '''
                streamer.send_data(frame, text)
                '''
                fps.update()
                '''
                if streamer.check_exit():
                    break
                '''
                
    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
