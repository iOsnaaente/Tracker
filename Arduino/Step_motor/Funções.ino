//DÁ UM PULSO NO MOTOR 
void pulse( byte stepperPin, byte vel ) {
  digitalWrite (stepperPin, HIGH);
  delayMicroseconds (vel);
  digitalWrite (stepperPin, LOW);
  delayMicroseconds (vel);
}

// DÁ N,M PASSOS NOS MOTORES NA DIREÇÃO DE DIR_n, DIR_m
void step( boolean dir_x, int steps_x, int vel_x, boolean dir_y,  int steps_y, int vel_y ) {
  digitalWrite( X_DIR, dir_x );
  digitalWrite( Y_DIR, dir_y );
  delay(1);
  for ( int i = 0; i < steps_x > steps_y ? steps_x : steps_y ; i++) {
    if ( steps_x > 0 ) {
      pulse( X_STP, vel_x );
      steps_x -= 1;
    }
    if (steps_y > 0 ) {
      pulse( Y_STP, vel_y );
      steps_y -= 1;
    }
  }
}

// ENVIA AS INFORMAÇÕES VIA SERIAL - COM CRC 
void send_data( int seg, int dias, float az, float alt, int p1, int p2 ) {
  CRC.add(seg); CRC.add(dias);
  CRC.add(az) ; CRC.add(alt);
  CRC.add(p1) ; CRC.add(p2);
  CRC_send = CRC.get_crc();

  int indx = 0;
  byte data[17];
  data[indx++] = (int)seg >>  8 ;
  data[indx++] = (int)seg & 0xff;
  data[indx++] = (int)dias >>  8 ;
  data[indx++] = (int)dias & 0xff;
  byte *f_pointer = (byte*)&az;
  for (int i = 0; i < sizeof(az); i++)
    data[indx++] = f_pointer[i];
  f_pointer = (byte*)&alt;
  for (int i = 0; i < sizeof(alt); i++)
    data[indx++] = f_pointer[i];
  data[indx++] = (int) p1 >> 8;
  data[indx++] = (int) p1 & 0xff;
  data[indx++] = (int) p2 >> 8;
  data[indx++] = (int) p2 & 0xff;
  data[indx++] = CRC_send;

  uint32_t page2send = ((int)pos.julianDay%(16384-1))*256;
  char data2send[255]; 
  for ( byte i = 0; i < 255; i++)
      data2send[i] = (i < 17) ? data[i] : 0x00;
  writePage( page2send, data2send );

  for ( int i=0; i<17; i++ )
    Serial.write( data[i] );
}


// PARA LER A SERIAL A CADA NOVO BYTE RECEBIDO 
void serialEvent() {
  while ( Serial.available()) {
    char received = (char) Serial.read();
    if ( received == '~' )
      string_complete = true;
    else
      string_receive += received;
  }
}
