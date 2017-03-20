package com.example.tomek.myapplication;

import android.hardware.Sensor;
import android.os.AsyncTask;
import android.os.Environment;

import java.io.File;
import java.io.FileWriter;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Created by tomek on 12/13/16.
 */

public class MyStorage {
    static private String fileDir;
    static private int NumOfElements = 1000;
    static private int FileLimitsPerDay = 100;
    static private String fileNameFormat="%d-%d-%d_accelerometer%d.xml";
    private ReentrantLock l;
    private String fileName;
    private File file;
    private FileWriter fileWriter;
    private boolean mediaMounted;
    private XYZAccelVectorBuff xyzAccelBuff;
    private int SensorType;
    private int noTasks;

    public MyStorage(int sensorType) {
        //mediaMounted = true;
        //fileDir="./";
        noTasks = 0;
        l = new ReentrantLock();
        SensorType = sensorType;
        mediaMounted = isExternalStorageWritable();
        File f = Environment.getExternalStorageDirectory();
        fileDir = f.getAbsolutePath();
        setFileName();
        openFile();
        writeXMLHeader();
    }

    public boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state)) {
            return true;
        }
        return false;
    }

    public int pushAccelVector(float x, float y, float z) {
        return this.pushAccelVectorTask( new XYZAccelVector( x,y,z,System.currentTimeMillis() ) );
    }

    public int pushAccelVectorTask(XYZAccelVector xyzAccelVector) {
        new NewXYZHandler().execute(xyzAccelVector);
        return ++noTasks; //not sync as not important
    }

    public void flushAccelVectors() {
        if (xyzAccelBuff==null) {
            return;
        }

        xyzAccelBuff.done();
        if (fileWriter!=null) {
            try {
                fileWriter.write("</AccelItems>");
                fileWriter.flush();
            } catch (Exception e) {
                //TODO: handle?
            }
        }
    }

    public void pushMessage(String message, long timestamp) {
        if (fileWriter == null)
            return;

        try {
            String msg = String.format("<Message msg=\"%s\" timestamp=\"%d\"/>",
                    message, timestamp);
            fileWriter.write(msg);
        } catch (Exception e) {
            //TODO: handle?
        }
    }

    public void done() {
        flushAccelVectors();
        closeFile();
    }

    public String getFileName() {
        return fileName;
    }

    private void enableXYZAccelVector() {
        l.lock();
        if (xyzAccelBuff == null ) {
            xyzAccelBuff = new XYZAccelVectorBuff(NumOfElements, fileWriter);
        }
        l.unlock();
    }

    private void writeXMLHeader() {
        if (SensorType==Sensor.TYPE_ACCELEROMETER) {
            writeToFile("<AccelItems type=\"Accelerometer\">\n");
        } else if (SensorType==Sensor.TYPE_LINEAR_ACCELERATION) {
            writeToFile("<AccelItems type=\"LinearAccelerometer\">\n");
        }
    }

    private void setFileName() {
        java.util.Calendar cal = java.util.Calendar.getInstance();
        int day = cal.get(java.util.Calendar.DAY_OF_MONTH);
        int month = cal.get(java.util.Calendar.MONTH);
        int year = cal.get(java.util.Calendar.YEAR);
        if (!fileDir.endsWith("/")) {
            fileDir += "/";
        }
        fileDir += "Download/";
        fileName = fileDir + String.format(fileNameFormat, year, month, day,0);
        file = new File(fileName);

        int c=1;
        while ((file.exists()) && (c < FileLimitsPerDay)) {
            fileName = fileDir + String.format(fileNameFormat, year, month, day,c);
            file = new File(fileName);
            c++;
        }
    }

    private void openFile() {
        if (mediaMounted && (file!=null)) {
            try {
                fileWriter = new FileWriter(file,true);
            } catch (Exception e) {
                //TODO
            }
        }
    }

    private void closeFile() {
        if (fileWriter!=null) {
            try {
                fileWriter.flush();
                fileWriter.close();
            } catch (Exception e) {
            }
        }
    }

    private void writeToFile(String str) {
        if (fileWriter!=null) {
            try {
                fileWriter.write(str);
            } catch(Exception e) {
                //TODO
            }
        }
    }

    private class NewXYZHandler extends AsyncTask<XYZAccelVector, Void, Void> {
        @Override
        protected Void doInBackground(XYZAccelVector... xyzAccelVectors) {
            int s = xyzAccelVectors.length;
            for(int i=0; i<s; i++) {
                enableXYZAccelVector();
                xyzAccelBuff.addAccelVector( xyzAccelVectors[i] );
            }
            noTasks--;
            return null;
        }
    }
}
