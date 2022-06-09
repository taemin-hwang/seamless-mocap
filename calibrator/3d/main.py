import sys
import calibrator as cb

if __name__ == "__main__":
    cali = cb.calibrator()

    if len(sys.argv) is 1:
        cam_id = 0
    else:
        cam_id = sys.argv[1]

    cali.initialize(cam_id)
    cali.run()
