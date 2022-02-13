void serializeData(){
  if (m == 0){
    Serial.print('c');
  }
}

void inversekinematics() {
  while (dataIn != 14){
    if (Serial.available() > 0) {
        dataIn = Serial.readString().toInt(); // i need to write a function that read my joint angle from inverse kinematics algorithm
        serializeData();
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

  }

}
