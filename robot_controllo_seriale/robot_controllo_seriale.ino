#include <Servo.h>
#include <SoftwareSerial.h>

Servo servo_b;
Servo servo_1;
Servo servo_2;
Servo servo_p1;
Servo servo_p2;
Servo servo_p3;

//SoftwareSerial Serial(2,3);

// Inserisco le variabili

int servobPos, servo1Pos, servo2Pos, servop1Pos, servop2Pos, servop3Pos; //posizione corrente
int servobPos2, servo1Pos2, servo2Pos2, servop1Pos2, servop2Pos2, servop3Pos2; //posizione prevista
int servobPos3[50], servo1Pos3[50], servo2Pos3[50], servop1Pos3[50], servop2Pos3[50], servop3Pos3[50]; //storing positions


int dataIn;
int m = 0;
int speedDelay = 30;
int index = 0;


void setup() {

  servo_b.attach(12); // motore della base
  servo_1.attach(11); // motore primo braccio
  servo_2.attach(4);  // motore secondo braccio
  servo_p1.attach(5); // motore polso
  servo_p2.attach(6); // motore supporto presa
  servo_p3.attach(9); // motore presa
  Serial.begin(9600);
  Serial.setTimeout(100);
  //Serial.begin(38400);
  //delay(25);


  // Posizione iniziale Robot
  servobPos2 = 90;
  servo_b.write(servobPos2);
  servo1Pos2 = 170; // fine corsa indietro
  servo_1.write(servo1Pos2);
  servo2Pos2 = 90; // incrementando si va verso il basso
  servo_2.write(servo2Pos2);
  servop1Pos2 = 130; // incrementando va verso destra
  servo_p1.write(servop1Pos2);
  servop2Pos2 = 90; // incrementando si alza
  servo_p2.write(servop2Pos2);
  servop3Pos2 = 160; // incrementando si apre
  servo_p3.write(servop3Pos2);

}


void runSteps() {
  while (dataIn != 14) {
    for (int i = 0; i <= index - 2; i++) {
      if (Serial.available() > 0) {
        dataIn = Serial.readString().toInt();
        if (dataIn == 16) {
          while (dataIn != 15) {
            if (Serial.available() > 0) {
              dataIn = Serial.readString().toInt();
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
          delay(speedDelay);
        }
      }
      if (servobPos3[i] < servobPos3[i + 1]) {
        for (int j = servobPos3[i]; j <= servobPos3[i + 1]; j++) {
          servo_b.write(j);
          delay(speedDelay);
        }
      }

      // Servo 1

      if (servo1Pos3[i] == servo1Pos3[i + 1]) {}
      if (servo1Pos3[i] > servo1Pos3[i + 1]) {
        for (int j = servo1Pos3[i]; j >= servo1Pos3[i + 1]; j--) {
          servo_1.write(j);
          delay(speedDelay);
        }
      }
      if (servo1Pos3[i] < servo1Pos3[i + 1]) {
        for (int j = servo1Pos3[i]; j <= servo1Pos3[i + 1]; j++) {
          servo_1.write(j);
          delay(speedDelay);
        }
      }

      // Servo 2

      if (servo2Pos3[i] == servo2Pos3[i + 1]) {}
      if (servo2Pos3[i] > servo2Pos3[i + 1]) {
        for (int j = servo2Pos3[i]; j >= servo2Pos3[i + 1]; j--) {
          servo_2.write(j);
          delay(speedDelay);
        }
      }
      if (servo2Pos3[i] < servo2Pos3[i + 1]) {
        for (int j = servo2Pos3[i]; j <= servo2Pos3[i + 1]; j++) {
          servo_2.write(j);
          delay(speedDelay);
        }
      }

      // Servo p1

      if (servop1Pos3[i] == servop1Pos3[i + 1]) {}
      if (servop1Pos3[i] > servop1Pos3[i + 1]) {
        for (int j = servop1Pos3[i]; j >= servop1Pos3[i + 1]; j--) {
          servo_p1.write(j);
          delay(speedDelay);
        }
      }
      if (servop1Pos3[i] < servop1Pos3[i + 1]) {
        for (int j = servop1Pos3[i]; j <= servop1Pos3[i + 1]; j++) {
          servo_p1.write(j);
          delay(speedDelay);
        }
      }

      // Servo p2

      if (servop2Pos3[i] == servop2Pos3[i + 1]) {}
      if (servop2Pos3[i] > servop2Pos3[i + 1]) {
        for (int j = servop2Pos3[i]; j >= servop2Pos3[i + 1]; j--) {
          servo_p2.write(j);
          delay(speedDelay);
        }
      }
      if (servop2Pos3[i] < servop2Pos3[i + 1]) {
        for (int j = servop2Pos3[i]; j <= servop2Pos3[i + 1]; j++) {
          servo_p2.write(j);
          delay(speedDelay);
        }
      }

      // Servo p3

      if (servop3Pos3[i] == servop3Pos3[i + 1]) {}
      if (servop3Pos3[i] > servop3Pos3[i + 1]) {
        for (int j = servop3Pos3[i]; j >= servop3Pos3[i + 1]; j--) {
          servo_p3.write(j);
          delay(speedDelay);
        }
      }
      if (servop3Pos3[i] < servop3Pos3[i + 1]) {
        for (int j = servop3Pos3[i]; j <= servop3Pos3[i + 1]; j++) {
          servo_p3.write(j);
          delay(speedDelay);
        }
      }
    } // chiude il ciclo for(int i)
  } // chiude il ciclo while(dataIn != 14)
}// chiude il void runSteps()


void loop() {

  if (Serial.available() > 0); {
    dataIn = Serial.readString().toInt();
    Serial.write(dataIn);
    if (dataIn == 1) {
      m = 1;
    }

    if (dataIn == 2) {
      m = 2;
    }

    if (dataIn == 3) {
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

    // move servomotors

    // motore PRESA
    // positive direction
    while (m == 1) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p3.write(servop3Pos2);
      servop3Pos2--;
      delay(speedDelay);
    }
    while (m == 2) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p3.write(servop3Pos2);
      servop3Pos2++;
      delay(speedDelay);
    }

    // motore polso su giu
    while (m == 3) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p2.write(servop2Pos2);
      servop2Pos2--;
      delay(speedDelay);
    }

    while (m == 4) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p2.write(servop2Pos2);
      servop2Pos2++;
      delay(speedDelay);
    }

    // Rollio polso
    while (m == 5) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p1.write(servop1Pos2);
      servop1Pos2--;
      delay(speedDelay);
    }
    while (m == 6) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_p1.write(servop1Pos2);
      servop1Pos2++;
      delay(speedDelay);
    }

    // Movimento gomito
    while (m == 7) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_2.write(servo2Pos2);
      servo2Pos2--;
      delay(speedDelay);
    }

    while (m == 8) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_2.write(servo2Pos2);
      servo2Pos2++;
      delay(speedDelay);
    }

    // Movimento SPALLA
    while (m == 9) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_1.write(servo1Pos2);
      servo1Pos2--;
      delay(speedDelay);
    }

    while (m == 10) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_1.write(servo1Pos2);
      servo1Pos2++;
      delay(speedDelay);
    }

    // Rotazione SPALLA
    while (m == 11) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_b.write(servobPos2);
      servobPos2--;
      delay(speedDelay);
    }

    while (m == 12) {
      if (Serial.available() > 0) {
        m = Serial.readString().toInt();
      }
      servo_b.write(servobPos2);
      servobPos2++;
      delay(speedDelay);
    }

    // last
    if (m == 13) {
      servobPos3[index] = servobPos2;
      servo1Pos3[index] = servo1Pos2;
      servo2Pos3[index] = servo2Pos2;
      servop1Pos3[index] = servop1Pos2;
      servop2Pos3[index] = servop2Pos2;
      servop3Pos3[index] = servop3Pos2;
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
  }
}
