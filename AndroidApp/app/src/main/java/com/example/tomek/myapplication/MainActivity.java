package com.example.tomek.myapplication;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.hardware.SensorEvent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.TextView;
import android.hardware.Sensor;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.content.Context;

import com.google.android.gms.appindexing.Action;
import com.google.android.gms.appindexing.AppIndex;
import com.google.android.gms.appindexing.Thing;
import com.google.android.gms.common.api.GoogleApiClient;

public class MainActivity extends AppCompatActivity
        implements View.OnClickListener,SensorEventListener {
    private static int Scale = 20;

    //UI
    private TextView accelX;
    private TextView accelY;
    private TextView accelZ;
    private TextView recordingOnOffInfo;
    private CheckBox useLinearAccel;
    private Button StartStopButton;
    private Boolean isRecording;
    private Boolean enableDrawing;
    private ImageView imgX;
    private ImageView imgY;
    private ImageView imgZ;
    private MyChart chartX;
    private MyChart chartY;
    private MyChart chartZ;
    private MyStorage myStorage;

    //Sensor
    private SensorManager mSensorManager;
    private Sensor mSensor;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        accelX = (TextView) findViewById(R.id.accelX);
        accelY = (TextView) findViewById(R.id.accelY);
        accelZ = (TextView) findViewById(R.id.accelZ);
        recordingOnOffInfo = (TextView) findViewById(R.id.recordingOnOffLabel);
        StartStopButton = (Button) findViewById(R.id.StartStopBtn);
        useLinearAccel = (CheckBox) findViewById(R.id.UseLinearAccel);
        isRecording = false;
        enableDrawing = false;
        StartStopButton.setOnClickListener(this);

        accelX.setText(String.format("X: %1$.3f", .0f));
        accelY.setText(String.format("Y: %1$.3f", .0f));
        accelZ.setText(String.format("Z: %1$.3f", .0f));

        imgX = (ImageView) findViewById(R.id.graphX);
        imgY = (ImageView) findViewById(R.id.graphY);
        imgZ = (ImageView) findViewById(R.id.graphZ);
        chartX = new MyChart(imgX);
        chartY = new MyChart(imgY);
        chartZ = new MyChart(imgZ);

        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
    }

    @Override
    protected void onStop() {
        /*if (isRecording) {
            isRecording = false;
            startStopRecording();
            updateLabels();
        }*/
        enableDrawing=false;
        super.onStop();
    }

    @Override
    protected void onResume() {
        super.onResume();
        enableDrawing=true;
    }

    @Override
    protected void onDestroy() {
        if (isRecording) {
            isRecording = false;
            startStopRecording();
            //updateLabels();
        }
        enableDrawing=false;
    }

    @Override
    public void onClick(View view) {
        isRecording = !isRecording;
        enableDrawing=isRecording;
        updateLabels();
        startStopRecording();
    }

    private Sensor getAccelerometer() {
        int accelType;
        if (useLinearAccel.isChecked()) {
            accelType = Sensor.TYPE_LINEAR_ACCELERATION;
        } else {
            accelType = Sensor.TYPE_ACCELEROMETER;
        }

        return mSensorManager.getDefaultSensor(accelType);
    }

    private void startStopRecording() {
        if (isRecording) {
            mSensor = getAccelerometer();
            myStorage = new MyStorage(mSensor.getType());
            mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_NORMAL);

        } else {
            mSensorManager.unregisterListener(this);
            if (myStorage!=null) {
                myStorage.done();
            }
            //closeFile();
        }
    }

    private void updateLabels() {
        if (isRecording) {
            StartStopButton.setText("Stop");
            recordingOnOffInfo.setText("Recording ON");
        } else {
            StartStopButton.setText("Start");
            recordingOnOffInfo.setText("Recording OFF");
        }
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        float x = sensorEvent.values[0];
        float y = sensorEvent.values[1];
        float z = sensorEvent.values[2];

        accelX.setText("X: "+String.valueOf(x));
        accelY.setText("Y: "+String.valueOf(y));
        accelZ.setText("Z: "+String.valueOf(z));
        chartX.addValue(x);
        chartY.addValue(y);
        chartZ.addValue(z);
        myStorage.pushAccelVector(x,y,z);
        draw();
    }


    private void draw() {
        if (enableDrawing) {
            chartX.draw();
            chartY.draw();
            chartZ.draw();
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {
        //not intrested
    }
}
