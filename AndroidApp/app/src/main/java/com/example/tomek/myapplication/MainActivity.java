package com.example.tomek.myapplication;

import android.hardware.SensorEvent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.hardware.Sensor;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.content.Context;

public class MainActivity extends AppCompatActivity
        implements View.OnClickListener, SensorEventListener {
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
    private LinearLayout imgX;
    private LinearLayout imgY;
    private LinearLayout imgZ;
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

        imgX = (LinearLayout) findViewById(R.id.graphX);
        imgY = (LinearLayout) findViewById(R.id.graphY);
        imgZ = (LinearLayout) findViewById(R.id.graphZ);
        chartX = new MyChart(this);
        imgX.addView(chartX);
        chartY = new MyChart(this);
        imgY.addView(chartY);
        chartZ = new MyChart(this);
        imgZ.addView(chartZ);

        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
    }

    @Override
    protected void onStop() {
        /*if (isRecording) {
            isRecording = false;
            startStopRecording();
            updateLabels();
        }*/
        enableDrawing = false;
        if ((myStorage != null) && (isRecording)) {
            myStorage.pushMessage("onStop:DrawingDisabled",
                    System.currentTimeMillis());
        }
        super.onStop();
    }

    @Override
    protected void onResume() {
        super.onResume();
        enableDrawing = true;
        if ((myStorage != null) && isRecording)
        myStorage.pushMessage("onResume:DrawingEnabled",
                System.currentTimeMillis());
    }

    @Override
    protected void onDestroy() {
        if (isRecording) {
            isRecording = false;
            startStopRecording();
            //updateLabels();
        }
        enableDrawing = false;
        super.onDestroy();
    }

    @Override
    public void onClick(View view) {
        isRecording = !isRecording;
        enableDrawing = isRecording;
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
            myStorage.pushMessage("New recording started", System.currentTimeMillis());
            mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_NORMAL);

        } else {
            mSensorManager.unregisterListener(this);
            if (myStorage != null) {
                myStorage.pushMessage("Recording done-finalizing", System.currentTimeMillis());
                myStorage.done();
            }
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

        int tasks = myStorage.pushAccelVector(x,y,z);
        accelZ.setText("Tasks: "+String.valueOf(tasks));
        updateUI(x,y,z);
    }

    @Override
    public void onStart() {
        super.onStart();
    }

    public void updateUI(float x, float y, float z) {
        chartX.addValue(x);
        chartY.addValue(y);
        chartZ.addValue(z);
        accelX.setText("X: " + String.valueOf(x));
        accelY.setText("Y: " + String.valueOf(y));
        //accelZ.setText("Z: " + String.valueOf(z));
        draw();
    }

    private void draw() {
        if (enableDrawing) {
            chartX.invalidate();
            chartY.invalidate();
            chartZ.invalidate();
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {
        //not intrested
    }

}
