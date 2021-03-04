package com.example.pointscanner;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.net.wifi.WifiInfo;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.app.ActivityCompat;

import org.apache.commons.net.ftp.FTPClient;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.NetworkInterface;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.TimeUnit;

import java.net.URL;
import java.net.HttpURLConnection;

// import com.example.pointscanner.R;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
  Context context;
  WifiManager wifiManager;
  WifiInfo wifiinfo;
 // TextView errors;
  Button Scan, Get, Send;
  boolean reached;
  String h = System.getProperty("line.separator");
  ListView lv;
  // private final int REQUEST_CODE_PERMISSION_FINE_LOC = 1;
  // private final int REQUEST_CODE_PERMISSION_WRITE = 2;
  List<ScanResult> results, resSend;
  String sense[], prom[];
  String tosend[], mean[];
  String mac;
  String cli_mac;
  String host;
  Integer port;
  String stringPort;
  File file;
  EditText editIP, editPort;
  Timer timer;
  TimerTask task;
  BufferedOutputStream os;
  BufferedInputStream is;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Toolbar toolbar = findViewById(R.id.toolbar);
    setSupportActionBar(toolbar);
    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
    context = getApplicationContext();
    wifiManager = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
    WifiInfo info = wifiManager.getConnectionInfo();
    cli_mac = info.getMacAddress();
    Scan = findViewById(R.id.Scan);
    Get = findViewById(R.id.Get);
    Send = findViewById(R.id.Send);
    lv = findViewById(R.id.list);
    // editX = findViewById(R.id.editX);
    // editY = findViewById(R.id.editY);
    editPort = findViewById(R.id.editPort);
    editIP = findViewById(R.id.editIP);
    Scan.setOnClickListener((View.OnClickListener) this);
    Get.setOnClickListener((View.OnClickListener) this);
    Send.setOnClickListener((View.OnClickListener) this);
    reached = false;
    onRequestPermissionsResult();
  }

  public static boolean hasPermissions(Context context, String... permissions) {
    if (context != null && permissions != null) {
      for (String permission : permissions) {
        if (ActivityCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED) {
          return false;
        }
      }
    }
    return true;
  }

  public void onRequestPermissionsResult() {
    int PERMISSION_ALL = 1;
    String[] PERMISSIONS = {
      android.Manifest.permission.WRITE_EXTERNAL_STORAGE,
      android.Manifest.permission.ACCESS_FINE_LOCATION,
    };
    if (!hasPermissions(this, PERMISSIONS)) {
      while (!hasPermissions(this, PERMISSIONS))
      //  onRequestPermissionsResult();
        ActivityCompat.requestPermissions(this, PERMISSIONS, PERMISSION_ALL);
    }
  }

  @RequiresApi(api = Build.VERSION_CODES.M)
  private void scanSuccess() {
    results = wifiManager.getScanResults();
    int r = results.size();
    int i = 0, v = 0;
    prom = new String[r];
    int freq;
    while (i < r) {
      if (results.get(i).level >= -75) {
        freq = results.get(i).frequency;
        mac = results.get(i).BSSID;
        prom[v] = ("SSID: " + results.get(i).SSID + "\r\nMAC: " + mac +
                  "\r\nRSSI: " + results.get(i).level + "\r\nFreq: " + freq);
        i++;
        v++;
      } else i++;
    }
    sense = new String[v];
    i = 0;
    while (i < v) {
      sense[i] = (prom[i]);
      i++;
    }
    lv.setAdapter(new ArrayAdapter<>(this, R.layout.row, sense));
  }

  @RequiresApi(api = Build.VERSION_CODES.M)
  private void scanSend() {
    BroadcastReceiver wifiScanReceiver = new BroadcastReceiver() {
      @RequiresApi(api = Build.VERSION_CODES.M)
      @Override
      public void onReceive(Context c, Intent intent) {
        boolean success = intent.getBooleanExtra(WifiManager.EXTRA_RESULTS_UPDATED, false);
        if (success) {
          sendSuccess();
        }
      }
    };
    IntentFilter intentFilter = new IntentFilter();
    intentFilter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
    context.registerReceiver(wifiScanReceiver, intentFilter);

    boolean success = wifiManager.startScan();
    if (success) {
      sendSuccess();
    }
  }

  @RequiresApi(api = Build.VERSION_CODES.M)
  private void sendSuccess() {
    resSend = wifiManager.getScanResults();
    int r = resSend.size();
    int i = 0, v = 0;
    tosend = new String[r];
    while (i < r) {
      if (resSend.get(i).level >= -75) {
        mac = resSend.get(i).BSSID;
        tosend[v] = ("AP: " + mac + " RSSI: " + resSend.get(i).level + "\r\n");
        i++;
        v++;
      } else i++;
    }
    mean = new String[v];
    i = 0;
    while (i < v) {
      mean[i] = (tosend[i]);
      i++;
    }
  }

  private void scanFailure() {
    if (results != null) {
      if (results.isEmpty())
        Toast.makeText(context,"Нет результатов", Toast.LENGTH_SHORT).show();
      else
        Toast.makeText(context,"Нет новых результатов, подождите", Toast.LENGTH_SHORT).show();
    }
    else  Toast.makeText(context,"Нет результатов", Toast.LENGTH_SHORT).show();
  }


  @Override
  public boolean onCreateOptionsMenu(Menu menu) {
  // Inflate the menu; this adds items to the action bar if it is present.
    getMenuInflater().inflate(R.menu.menu_main, menu);
    return true;
  }

  @Override
  public boolean onOptionsItemSelected(MenuItem item) {
  // Handle action bar item clicks here. The action bar will
  // automatically handle clicks on the Home/Up button, so long
  // as you specify a parent activity in AndroidManifest.xml.
    int id = item.getItemId();
  //noinspection SimplifiableIfStatement
    if (id == R.id.action_settings) {
      return true;
    }
    return super.onOptionsItemSelected(item);
  }

  @RequiresApi(api = Build.VERSION_CODES.M)
  public void onClick(View v) {
    switch ((v.getId())) {
      case R.id.Scan: {
        BroadcastReceiver wifiScanReceiver = new BroadcastReceiver() {
          @RequiresApi(api = Build.VERSION_CODES.M)
          @Override
          public void onReceive(Context c, Intent intent) {
            boolean success = intent.getBooleanExtra(WifiManager.EXTRA_RESULTS_UPDATED, false);
            if (success) {
              scanSuccess();
            } else {
              scanFailure();
            }
          }
        };
        IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
        context.registerReceiver(wifiScanReceiver, intentFilter);
        boolean success = wifiManager.startScan();
        if (success) {
          scanSuccess();
        } else scanFailure();
        break;
      }

      case R.id.Get: {
        host = editIP.getText().toString();
        stringPort = editPort.getText().toString();
        // TODO: Getting mac and send it to server

        try {
          URL url = new URL("http://"+host+":"+stringPort+"/api/v1/get/vector?mac="+cli_mac);
          HttpURLConnection clientAPIv1 = (HttpURLConnection) url.openConnection();
          String transaction_result = "We got error";
          if (clientAPIv1.getResponseCode() == HttpURLConnection.HTTP_OK) {
          //if success
            BufferedReader in = new BufferedReader(new InputStreamReader(clientAPIv1.getInputStream()));
            transaction_result = in.readLine();
            in.close();
          }
          Toast.makeText(context,transaction_result, Toast.LENGTH_SHORT).show();
          } catch (Exception e) {
            e.printStackTrace();
          }
        break;
      }

      case R.id.Send: {
        host = editIP.getText().toString();
        stringPort = editPort.getText().toString();
        // TODO: Getting mac and send it to server

        try {
          URL url = new URL("http://"+host+":"+stringPort+"/api/v1/set/vector");
          HttpURLConnection clientAPIv1 = (HttpURLConnection) url.openConnection();
          String transaction_result = "We got error";
          if (clientAPIv1.getResponseCode() == HttpURLConnection.HTTP_OK) {
          //if success
            BufferedReader in = new BufferedReader(new InputStreamReader(clientAPIv1.getInputStream()));
            transaction_result = in.readLine();
            in.close();
          }
          Toast.makeText(context,transaction_result, Toast.LENGTH_SHORT).show();
          } catch (Exception e) {
            e.printStackTrace();
          }
        break;
      }
    }
  }
}
