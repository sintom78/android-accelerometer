package com.example.tomek.myapplication;

/**
 * Created by tomek on 12/11/16.
 */

public class RingBuffer {
    private float elements[];
    private int head;
    private int tail;
    private int size;

    public RingBuffer(int size) {
        elements = new float[size];
        this.size = size;
        head = 0;
        tail = 0;
    }

    public void pushElement(float value) {
        elements[head] = value;
        head++;
        if (head==size) {
            head = 0;
        }
        if (head==tail) {
            tail++;
            if (tail==size) {
                tail = 0;
            }
        }
    }

    public int getCount() {
        int count;
        if (head >= tail) {
            count = head - tail;
        } else {
            count = (size - tail) + head;
        }
        return count;
    }

    public float getElementByIdx(int index) {
        if (index >= size) {
            throw new IndexOutOfBoundsException();
        }

        int idx = tail + index;
        if (idx >= size) {
            idx -= size;
        }

        return  elements[idx];
    }
}
