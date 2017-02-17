package com.example.tomek.myapplication;

import java.util.Date;

class XYZAccelVector {
    private float x;
    private float y;
    private float z;
    private long timestamp;

    public XYZAccelVector(float x, float y, float z, long timestamp)
    {
        this.x=x;
        this.y=y;
        this.z=z;
        this.timestamp = timestamp;// System.currentTimeMillis();
    }

    public String getXMLString()
    {
        return String.format("<AccelItem data=\"%d\" x=\"%f\" y=\"%f\" z=\"%f\"/>\n",
                             timestamp, x, y, z);
    }

    public float getX()
    {
        return x;
    }

    public float getY()
    {
        return y;
    }

    public float getZ()
    {
        return z;
    }

    public Date getDate()
    {
        return new Date(timestamp);
    }

    public long getTime()
    {
        return timestamp;
    }
}
