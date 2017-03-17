package com.example.tomek.myapplication;

import java.io.FileWriter;
import java.util.concurrent.locks.ReentrantLock;

class XYZAccelVectorBuff {
    private XYZAccelVector buff1[];
    private XYZAccelVector buff2[];
    private XYZAccelVector currentBuff[];
    private XYZAccelVector backBuff[];
    private int buf_elements;
    private int current_element;
    private FileWriter fileWriter;
    private ReentrantLock lock;

    public XYZAccelVectorBuff(int elements, FileWriter fw)
    {
        lock = new ReentrantLock();

        buff1 = new XYZAccelVector[elements];
        buff2 = new XYZAccelVector[elements];
        currentBuff = buff1;
        fileWriter = fw;
        buf_elements = elements;
    }

    public void swapBuff()
    {
       if (currentBuff == buff1)
       {
           backBuff = buff1;
           currentBuff = buff2;
           current_element = 0;
       } else {
           backBuff = buff2;
           currentBuff = buff1;
           current_element = 0;
       }
    }

    private void flushBuffElementsToFile(XYZAccelVector[] buff, int noElements)
    {
        if (fileWriter==null) {
            return;
        }

        String str = new String();
            
        for(int c = 0; c < noElements; c++) {
            XYZAccelVector vec = buff[c];
            str += "    " + vec.getXMLString();
        }

        if (!str.isEmpty()) {
            try {
                fileWriter.write(str);
            } catch (Exception e) {
                //TODO: handle exception
                System.out.println("Exception " + e);
            }
        } else {
            System.out.println("str is empty");
        }
    }

    public void flushBackBuff()
    {
        flushBuffElementsToFile(backBuff,buf_elements);
    }

    public void addAccelVector(XYZAccelVector vec)
    {
        lock.lock();
        try {
            currentBuff[current_element] = vec;
            current_element++;
            if (current_element == buf_elements) {
                swapBuff();
                flushBackBuff();
            }
        } finally {
            lock.unlock();
        }
    }
        
    public void done() {
        if (fileWriter==null) {
            return;
        }

        flushBuffElementsToFile(currentBuff,current_element);
        try {
            fileWriter.flush();
        } catch (Exception e) {
        }
    }
}
