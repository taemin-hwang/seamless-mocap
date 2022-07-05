import os.path
import numpy as np
import cv2

class FileStorage(object):
    def __init__(self, filename, isWrite=False):
        version = cv2.__version__
        self.major_version = int(version.split('.')[0])
        self.second_version = int(version.split('.')[1])

        if isWrite:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
        else:
            self.fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)

    def __del__(self):
        cv2.FileStorage.release(self.fs)

    def write(self, key, value, dt='mat'):
        if dt == 'mat':
            cv2.FileStorage.write(self.fs, key, value)
        elif dt == 'list':
            if self.major_version == 4: # 4.4
                self.fs.startWriteStruct(key, cv2.FileNode_SEQ)
                for elem in value:
                    self.fs.write('', elem)
                self.fs.endWriteStruct()
            else: # 3.4
                self.fs.write(key, '[')
                for elem in value:
                    self.fs.write('none', elem)
                self.fs.write('none', ']')

    def read(self, key, dt='mat'):
        if dt == 'mat':
            output = self.fs.getNode(key).mat()
        elif dt == 'list':
            results = []
            n = self.fs.getNode(key)
            for i in range(n.size()):
                val = n.at(i).string()
                if val == '':
                    val = str(int(n.at(i).real()))
                if val != 'none':
                    results.append(val)
            output = results
        else:
            raise NotImplementedError
        return output

    def close(self):
        self.__del__(self)

def read_camera(intri_path, extri_path):
  assert os.path.exists(intri_path), intri_path
  assert os.path.exists(extri_path), extri_path

  intri = FileStorage(intri_path)
  extri = FileStorage(extri_path)
  cams, P = {}, {}
  cam_names = intri.read('names', dt='list')
  for cam in cam_names:
      cams[cam] = {}
      cams[cam]['K'] = intri.read('K_{}'.format( cam))
      cams[cam]['invK'] = np.linalg.inv(cams[cam]['K'])
      Rvec = extri.read('R_{}'.format(cam))
      Tvec = extri.read('T_{}'.format(cam))
      R = cv2.Rodrigues(Rvec)[0]
      RT = np.hstack((R, Tvec))

      cams[cam]['RT'] = RT
      cams[cam]['R'] = R
      cams[cam]['T'] = Tvec
      P[cam] = cams[cam]['K'] @ cams[cam]['RT']
      cams[cam]['P'] = P[cam]

      cams[cam]['dist'] = intri.read('dist_{}'.format(cam))
  cams['basenames'] = cam_names
  return cams

def print_camera_parameter(cams):
  for i in range(1, 5):
    print('CAM # : ', i, ' ============================================================ ')
    print('   K  : ', cams[str(i)]['K'])
    print('   RT : ', cams[str(i)]['RT'])
    print('   P : ', cams[str(i)]['P'])