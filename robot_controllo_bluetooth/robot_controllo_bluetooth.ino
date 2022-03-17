#include <Servo.h>
#include <SoftwareSerial.h>


Servo servo_b;
Servo servo_1;
Servo servo_2;
Servo servo_p1;
Servo servo_p2;
Servo servo_p3;

SoftwareSerial Bluetooth(2,3);

// Inserisco le variabili

int servobPos, servo1Pos, servo2Pos, servop1Pos, servop2Pos, servop3Pos; 
// servobPos, servo1Pos, servo2Pos, servop1Pos, servop2Pos, servop3Pos --- corrispondenza con indici array; 
int current_angle[6] ={}; //posizione corrente 
int servobPos3[50], servo1Pos3[50], servo2Pos3[50], servop1Pos3[50], servop2Pos3[50], servop3Pos3[50]; //storing positions
bool state = true;
int angles[5] = {};
String prova_split[5] = {};



int dataIn;
int m = 0;
int speedDelayManual = 30;
int speedDelay = 10;
int index = 0;
int index_inverse = 0;
bool running_kinematic = false;

void setup() {

  servo_b.attach(12); // motore della base
  servo_1.attach(11); // motore primo braccio
  servo_2.attach(5);  // motore secondo braccio
  servo_p1.attach(6); // motore polso
  servo_p2.attach(8); // motore supporto presa
  servo_p3.attach(9); // motore presa
  Serial.begin(38400);
  Bluetooth.begin(38400);
  Bluetooth.setTimeout(10);
  delay(25);


  // Posizione iniziale Robot
  current_angle[0] = 90;
  servo_b.write(current_angle[0]);
  current_angle[1] = 110; // fine corsa indietro
  servo_1.write(current_angle[1]);
  current_angle[2] = 180; // incrementando si va verso il basso
  servo_2.write(current_angle[2]);
  current_angle[3] = 90; // incrementando va verso destra
  servo_p1.write(current_angle[3]);
  current_angle[4] = 0; // incrementando si alza
  servo_p2.write(current_angle[4]);
  current_angle[5] = 160; // incrementando si apre
  servo_p3.write(current_angle[5]);

}

void runSteps() {
  while (dataIn != 14) {
    for (int i = 0; i <= index - 2; i++) {
      if (Bluetooth.available() > 0) {
        dataIn = Bluetooth.readString().toInt();
        if (dataIn == 16) {
          while (dataIn != 15) {
            if (Bluetooth.available() > 0) {
              dataIn = Bluetooth.readString().toInt();
              if (dataIn == 14) {
                break;
              }
            }
          }
        }
      }
      // Servo base

      if (servobPos3[i] == servobPos3[i + 1]) {}
      if (servobPos3[i] > servobPos3[i + 1]) {
        for (int j = servobPos3[i]; j >= servobPos3[i + 1]; j--) {
          servo_b.write(j);
          delay(speedDelayManual);
        }
      }
      if (servobPos3[i] < servobPos3[i + 1]) {
        for (int j = servobPos3[i]; j <= servobPos3[i + 1]; j++) {
          servo_b.write(j);
          delay(speedDelayManual);
        }
      }

      // Servo 1

      if (servo1Pos3[i] == servo1Pos3[i + 1]) {}
      if (servo1Pos3[i] > servo1Pos3[i + 1]) {
        for (int j = servo1Pos3[i]; j >= servo1Pos3[i + 1]; j--) {
          servo_1.write(j);
          delay(speedDelayManual);
        }
      }
      if (servo1Pos3[i] < servo1Pos3[i + 1]) {
        for (int j = servo1Pos3[i]; j <= servo1Pos3[i + 1]; j++) {
          servo_1.write(j);
          delay(speedDelayManual);
        }
      }

      // Servo 2

      if (servo2Pos3[i] == servo2Pos3[i + 1]) {}
      if (servo2Pos3[i] > servo2Pos3[i + 1]) {
        for (int j = servo2Pos3[i]; j >= servo2Pos3[i + 1]; j--) {
          servo_2.write(j);
          delay(speedDelayManual);
        }
      }
      if (servo2Pos3[i] < servo2Pos3[i + 1]) {
        for (int j = servo2Pos3[i]; j <= servo2Pos3[i + 1]; j++) {
          servo_2.write(j);
          delay(speedDelayManual);
        }
      }

      // Servo p1

      if (servop1Pos3[i] == servop1Pos3[i + 1]) {}
      if (servop1Pos3[i] > servop1Pos3[i + 1]) {
        for (int j = servop1Pos3[i]; j >= servop1Pos3[i + 1]; j--) {
          servo_p1.write(j);
          delay(speedDelayManual);
        }
      }
      if (servop1Pos3[i] < servop1Pos3[i + 1]) {
        for (int j = servop1Pos3[i]; j <= servop1Pos3[i + 1]; j++) {
          servo_p1.write(j);
          delay(speedDelayManual);
        }
      }

      // Servo p2

      if (servop2Pos3[i] == servop2Pos3[i + 1]) {}
      if (servop2Pos3[i] > servop2Pos3[i + 1]) {
        for (int j = servop2Pos3[i]; j >= servop2Pos3[i + 1]; j--) {
          servo_p2.write(j);
          delay(speedDelayManual);
        }
      }
      if (servop2Pos3[i] < servop2Pos3[i + 1]) {
        for (int j = servop2Pos3[i]; j <= servop2Pos3[i + 1]; j++) {
          servo_p2.write(j);
          delay(speedDelayManual);
        }
      }

      // Servo p3

      if (servop3Pos3[i] == servop3Pos3[i + 1]) {}
      if (servop3Pos3[i] > servop3Pos3[i + 1]) {
        for (int j = servop3Pos3[i]; j >= servop3Pos3[i + 1]; j--) {
          servo_p3.write(j);
          delay(speedDelayManual);
        }
      }
      if (servop3Pos3[i] < servop3Pos3[i + 1]) {
        for (int j = servop3Pos3[i]; j <= servop3Pos3[i + 1]; j++) {
          servo_p3.write(j);
          delay(speedDelayManual);
        }
      }
    } // chiude il ciclo for(int i)
  } // chiude il ciclo while(dataIn != 14)
}// chiude il void runSteps()

void loop() {

  if (Bluetooth.available() > 0); {
    dataIn = Bluetooth.readString().toInt();
    if (dataIn != 0){
    Serial.print("data in equals: ") ;
    Serial.println(dataIn);
    }
    if (dataIn == 1) {
      m = 1;
    }

    if (dataIn == 2) {
      m = 2;
    }

    if (dataIn == 3) {
      Serial.println("modifico m = 3");
      m = 3;
    }

    if (dataIn == 4) {
      m = 4;
    }

    if (dataIn == 5) {
      m = 5;
    }

    if (dataIn == 6) {
      m = 6;
    }

    if (dataIn == 7) {
      m = 8;
    }

    if (dataIn == 8) {
      m = 7;
    }

    if (dataIn == 9) {
      m = 9;
    }

    if (dataIn == 10) {
      m = 10;
    }

    if (dataIn == 11) {
      m = 11;
    }

    if (dataIn == 12) {
      m = 12;
    }
    if (dataIn == 13) {
      m = 13;
    }

    if (dataIn == 14) {
      m = 14;
    }

    if (dataIn == 15) {
      m = 15;
    }

    if (dataIn == 16) {
      m = 16;
    }

    if (dataIn == 17) {
      m = 17;
    }
    if (dataIn == 35){
      m = 35;
    }
    // move servomotors

    // motore PRESA
    // positive direction
    while (m == 1) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p3.write(current_angle[5]);
      if (current_angle[5] > 0)
      {
        Bluetooth.println(m);
        current_angle[5]--;
        delay(speedDelayManual);
      }
    }
    while (m == 2) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p3.write(current_angle[5]);
      if (current_angle[5] < 180)
      {
        Bluetooth.println(m);
        current_angle[5]++;
        delay(speedDelayManual);
      }
    }

    // motore polso su giu
    while (m == 3) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p2.write(current_angle[4]);
      if (current_angle[4] > 0)
      {
        Bluetooth.println(m);
        current_angle[4]--;
        delay(speedDelayManual);
      }
    }

    while (m == 4) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p2.write(current_angle[4]);
      if (current_angle[4] < 180)
      {
        Bluetooth.println(m);
        current_angle[4]++;
        delay(speedDelayManual);
      }
    }

    // Rollio polso
    while (m == 5) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p1.write(current_angle[3]);
      if (current_angle[3] > 0)
      {
        Bluetooth.println(m);
        current_angle[3]--;
        delay(speedDelayManual);
      }
    }
    while (m == 6) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_p1.write(current_angle[3]);
      if (current_angle[3] < 180)
      {
        Bluetooth.println(m);
        current_angle[3]++;
        delay(speedDelayManual);
      }
    }

    // Movimento gomito
    while (m == 7) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_2.write(current_angle[2]);
      if (current_angle[2] > 0)
      {
        Bluetooth.println(m);
        current_angle[2]--;
        delay(speedDelayManual);
      }
    }

    while (m == 8) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_2.write(current_angle[2]);
      if (current_angle[2] < 180)
      {
        Bluetooth.println(m);
        current_angle[2]++;
        delay(speedDelayManual);
      }
    }

    // Movimento SPALLA
    while (m == 9) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_1.write(current_angle[1]);
      if (current_angle[1] > 0)
      {
        Bluetooth.println(m);
        current_angle[1]--;
        delay(speedDelayManual);
      }
    }

    while (m == 10) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_1.write(current_angle[1]);
      if (current_angle[1] < 180)
      {
        Bluetooth.println(m);
        current_angle[1]++;
        delay(speedDelayManual);
      }
    }

    // Rotazione SPALLA
    while (m == 11) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_b.write(current_angle[0]);
      if (current_angle[0] > 0)
      {
        Bluetooth.println(m);
        current_angle[0]--;
        delay(speedDelayManual);
      }
    }

    while (m == 12) {
      if (Bluetooth.available() > 0) {
        m = Bluetooth.readString().toInt();
      }
      servo_b.write(current_angle[0]);
      if (current_angle[0] < 180)
      {
        Bluetooth.println(m);
        current_angle[0]++;
        delay(speedDelayManual);
      }
    }

    // last
    if (m == 13) {
      servobPos3[index] = current_angle[0];
      servo1Pos3[index] = current_angle[1];
      servo2Pos3[index] = current_angle[2];
      servop1Pos3[index] = current_angle[3];
      servop2Pos3[index] = current_angle[4];
      servop3Pos3[index] = current_angle[5];
      index++;
      m = 0;
    }

    if (m == 15) {
      runSteps();
    }

    if ( m == 14) {

      memset(servobPos3, 0, sizeof(servobPos3));
      memset(servo1Pos3, 0, sizeof(servo1Pos3));
      memset(servo2Pos3, 0, sizeof(servo2Pos3));
      memset(servop1Pos3, 0, sizeof(servop1Pos3));
      memset(servop2Pos3, 0, sizeof(servop2Pos3));
      memset(servop3Pos3, 0, sizeof(servop3Pos3));
      index = 0;
    }

    if (m == 17) {
      //Bluetooth.println("s");
      run_kinematics_motion();
      m = 0;
      state = true;
    }

    if (m == 35) {
      Bluetooth.println(m);
      delay(30);
      for (int i = 0;i <6;i++){
        Bluetooth.print(current_angle[i]);
        delay(30);
      }
      m=0;
    }
  }
}
