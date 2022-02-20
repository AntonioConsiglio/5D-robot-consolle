void run_kinematics_motion() 
{
  bool servb_done = false;
  bool serv1_done = false;
  bool serv2_done = false;
  bool servp1_done = false;
  bool servp2_done = false;
  while (state) 
  {
    if (Bluetooth.available() > 0) 
    {
      dataIn = Bluetooth.readString().toInt(); 
      if (dataIn != 255) 
      {
        if (index_inverse < 5)
        {
          angles[index_inverse] = dataIn;
          //Serial.println("angoli salvati: "+String(angles[index_inverse])+" indice: "+String(index_inverse));
          index_inverse++;
        }
        if (index_inverse == 5) 
        {
          state = false;
          index_inverse = 0;
          running_kinematic = true;
        }
      }
      else state = false;
    }
  }
  while (running_kinematic)
  {
    if (servb_done and serv1_done and serv2_done and servp1_done and servp2_done)
    {
      //Serial.println("Posizione raggiunta !!");
      running_kinematic = false;
      angles[5] = {};
      servb_done = false;
      serv1_done = false;
      serv2_done = false;
      servp1_done = false;
      servp2_done = false;
    }
    else
    {
      for (int j=0;j<5;j++)
      {
        switch (j){
        //Serial.println("siamo a questo caso"+String(j));
        case 0:
          if (current_angle[j] < angles[j] and j == 0)
          {
            current_angle[j]=current_angle[j]+1;
            //Serial.println("current angle base: "+String(current_angle[j]));
            servo_b.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] > angles[j] and j == 0)
          {
            current_angle[j]=current_angle[j]-1;
            servo_b.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] == angles[j] and j == 0)
          {
            servb_done = true;
            //Serial.println("servo b done!");
            break;
          }
        case 1:
          if (current_angle[j] < angles[j] and j == 1)
          {
            current_angle[j]=current_angle[j]+1;
            servo_1.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] > angles[j] and j == 1)
          {
            current_angle[j]=current_angle[j]-1;
            servo_1.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] == angles[j] and j == 1)
          {
            //Serial.println("servo 1 done!");
            serv1_done = true;
            break;
          }
        case 2:
          if (current_angle[j] < angles[j] and j == 2)
          {
            current_angle[j]=current_angle[j]+1;
            servo_2.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] > angles[j] and j == 2)
          {
            current_angle[j]=current_angle[j]-1;
            servo_2.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] == angles[j] and j == 2)
          {
            //Serial.println("servo 2 done!");
            serv2_done = true;
            break;
          }
        case 3:
          if (current_angle[j] < angles[j] and j == 3)
          {
            current_angle[j]=current_angle[j]+1;
            //Serial.println("current angle p1: "+String(current_angle[j]));
            servo_p1.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] > angles[j] and j == 3)
          {
            current_angle[j]=current_angle[j]-1;
            servo_p1.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] == angles[j] and j == 3)
          {
            //Serial.println("servo p1 done!");
            servp1_done = true;
            break;
          }
        case 4:
          if (current_angle[j] < angles[j] and j == 4)
          {
            current_angle[j]=current_angle[j]+1;
            servo_p2.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] > angles[j] and j == 4)
          {
            current_angle[j]=current_angle[j]-1;
            servo_p2.write(current_angle[j]);
            delay(speedDelay);
          }
          else if (current_angle[j] == angles[j] and j == 4)
          {
           //Serial.println("servo p2 done!");
           servp2_done=true;
           break;
          }        
        }
      }
    }
  }
}
