package com.example.tomek.myapplication;

/**
 * Created by tomek on 12/11/16.
 */

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.View;

public class MyChart extends View {

    static float Scale = 10.f;
    static int BgColor = 0x00AAAAAA;
    static int LineColor = 0xFFFF0000;

    private RingBuffer buffer;
    private Paint paint;
    private int OY;
    private int height;

    public MyChart(Context context) {
        super(context);
    }

    public void addValue(float val) {
        buffer.pushElement(val);
    }

    public float getCurrentValue() {
        float retVal = 0;
        if (buffer.getCount() > 0) {
            retVal = buffer.getCurrentValue();
        }

        return retVal;
    }

    //@Override
    void OnDraw(Canvas canvas) {
        if (buffer!=null && canvas !=null) {
            draw(canvas);
        }
    }

    public void draw(Canvas canvas) {
        canvas.drawColor(BgColor);
        int vals = buffer.getCount();
        for (int c = 1; c < vals; c++) {
            float sx = c - 1;
            float sy = OY + Scale * buffer.getElementByIdx(c - 1);
            float ey = OY + Scale * buffer.getElementByIdx(c);
            canvas.drawLine(sx, sy, c, ey, paint);
        }
    }

    @Override
    public void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w,h,oldw,oldh);
        height = w;
        OY=h/2;
        if ((height>0) && (h>0)) {
            buffer = new RingBuffer(height);
            paint = new Paint();
            paint.setColor(LineColor);
        }
    }
}
