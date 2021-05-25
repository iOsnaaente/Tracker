class CRC8 {
    uint8_t crc;
  public:
    CRC8() {
      this->crc = 0x00;
    }
    
    void add( int value ) {
      union {
        int in_val;
        byte out_val[sizeof(int)];
      } u_val;
      u_val.in_val = value;
      for ( int i = 0; i < sizeof(int); i++)
        this->crc = (uint8_t)( this->crc + u_val.out_val[i]);
    }
    
    void add( float value ) {
      union {
        float in_val;
        byte out_val[sizeof(float)];
      } u_val;
      u_val.in_val = value;
      for ( int i = 0; i < sizeof(float); i++)
        this->crc = (uint8_t)( this->crc + u_val.out_val[i]);
    }
    
    void add( double value ) {
      union {
        double in_val;
        byte out_val[sizeof(double)];
      } u_val;
      u_val.in_val = value;
      for ( int i = 0; i < sizeof(double); i++)
        this->crc = (uint8_t)( this->crc + u_val.out_val[i]);
    }
    
    void add( long int value ) {
      union {
        long int in_val;
        byte out_val[sizeof(long int)];
      } u_val;
      u_val.in_val = value;
      for ( int i = 0; i < sizeof(long int); i++)
        this->crc = (uint8_t)( this->crc + u_val.out_val[i]);
    }
};
