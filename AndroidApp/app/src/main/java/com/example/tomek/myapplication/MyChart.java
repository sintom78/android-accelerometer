package com.example.tomek.myapplication;

/**
 * Created by tomek on 12/11/16.
 */

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.View;
import android.widget.ImageView;

public class MyChart implements View.OnLayoutChangeListener  {

    static float Scale = 10.f;
    static int BgColor = 0xAAAAAAAA;
    static int LineColor = 0xFFFF0000;

    private ImageView image;
    private Bitmap bitmap;
    private Canvas canvas;
    private RingBuffer buffer;
    private Paint paint;
    private int OY;
    private int height;

    public MyChart(ImageView image) {
        this.image = image;
        image.addOnLayoutChangeListener(this);
    }

    public void addValue(float val) {
        buffer.pushElement(val);
    }

    public void draw() {
        if (canvas == null)
            return;

        canvas.drawColor(BgColor);
        int vals = buffer.getCount();
        for (int c = 1; c < vals; c++) {
            float sx = c - 1;
            float sy = OY + Scale * buffer.getElementByIdx(c - 1);
            float ey = OY + Scale * buffer.getElementByIdx(c);
            canvas.drawLine(sx, sy, c, ey, paint);
        }
        image.setImageBitmap(bitmap);
    }

    @Override
    public void onLayoutChange(View view, int i, int i1, int i2, int i3, int i4, int i5, int i6, int i7) {
        if ((view==image) && bitmap==null) {
            height = view.getWidth();
            int h = view.getHeight();
            OY=h/2;
            if ((height>0) && (h>0)) {
                buffer = new RingBuffer(height);
                bitmap = Bitmap.createBitmap(height, h, Bitmap.Config.ARGB_8888);
                canvas = new Canvas(bitmap);
                paint = new Paint();
                paint.setColor(LineColor);
            }
        }

    }
}
