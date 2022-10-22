void split_string_by(String to_split,char splitter)
{
  int lunghezza = to_split.length();
  int index[7] = {0};
  int j = 1;
  if (lunghezza > 1){
    //Serial.println(to_split);
  for(int i=0;i< lunghezza;i++)
  {
    if (to_split[i] == splitter){
      index[j] = i;
//      Serial.println(i);
//      Serial.println("INDEX: ");
//      Serial.println(index[j]);
      j++;
    }
    index[j] = lunghezza;
   
  }
  for (int k=0;k<6;k++)
  {
   //Serial.println("INDEX FOR SPLITTING");
   //Serial.println(index[k]);
   //Serial.println(index[k+1]);
   if (k == 0){
   angles[k] = to_split.substring(index[k],index[k+1]).toInt();
   //Serial.println(prova_split[k]);}
   }
   else{
    angles[k] = to_split.substring(index[k]+1,index[k+1]).toInt();
   //Serial.println(prova_split[k]);
   }
  }
}
}

void run_kinematics_motion(bool home) 
{
  bool servb_done = false;
  bool serv1_done = false;
  bool serv2_done = false;
  bool servp1_done = false;
  bool servp2_done = false;
  bool state = true;
  while (state) 
  {
    if (home)
    {
      state = false;
      index_inverse = 0;
      running_kinematic = true;
      for (int ang=0;ang<6;ang++)
      {
        angles[ang] = home_angles[ang];
      }

    }
    else if (Bluetooth.available() > 0) 
    {
      String datas = Bluetooth.readString();
      split_string_by(datas,',');
      state = false;
      index_inverse = 0;
      running_kinematic = true;
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
      if (home){
      Bluetooth.println("555");}
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
