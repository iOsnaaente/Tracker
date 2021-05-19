/// Definição dos parametros para seguir o sol

struct STLocation loc  ; 
struct STPosition pos  ;
struct STTime     time ; 


int useDegrees            = true ;         
int useNorthEqualsZero    = false ;     
int computeRefrEquatorial = false ;  
int computeDistance       = false ;        

//loc.latitude    = -29.165307659422155 ;
//loc.longitude   = -54.89831672609559 ;

//loc.pressure    = 101.0 ;                 // Pressão atmosférica em Kpa
//loc.temperature  = 298.0 ;                   // Temperatura ambiente de 25ºC em K 

float azimute; 
float altitude; 

void get_sun_position(int year, int month, int day, int hour, int minute, double second){
  time.year   = year ;
  time.month  = month ;
  time.day    = day ;
  time.hour   = hour ; 
  time.minute = minute ;
  time.second = second ;

  SolTrack( time, loc, &pos, useDegrees, useNorthEqualsZero, computeRefrEquatorial, computeDistance); 

  azimute  = pos.azimuthRefract;
  altitude = pos.altitudeRefract; 
  
}


# define X_DIR  5  // X -axis stepper motor direction control
# define Y_DIR  6  // y -axis stepper motor direction control
# define X_STP  2  // x -axis stepper control
# define Y_STP  3  // y -axis stepper control

# define EN 8      // stepper motor enable , active low

String string_receive = "";  

bool string_complete = false; 

void pulse( byte stepperPin, byte vel ){
  digitalWrite (stepperPin, HIGH);
  delayMicroseconds (vel);
  digitalWrite (stepperPin, LOW);
  delayMicroseconds (vel);  
}

void step( boolean dir_x, int steps_x, int vel_x, boolean dir_y,  int steps_y, int vel_y ){
  digitalWrite( X_DIR, dir_x );
  digitalWrite( Y_DIR, dir_y ); 
  delay(1); 
  for ( int i = 0; i < steps_x > steps_y ? steps_x : steps_y ; i++){
    if ( steps_x > 0 ){
      pulse( X_STP, vel_x );
      steps_x -= 1; 
    } 
    if (steps_y > 0 ){
      pulse( Y_STP, vel_y ); 
      steps_y -= 1; 
    }
  }
}

void setup () {
  // Definição dos pinos de saida e entrada 
  pinMode (X_DIR, OUTPUT); pinMode (X_STP, OUTPUT);
  pinMode (Y_DIR, OUTPUT); pinMode (Y_STP, OUTPUT);
  pinMode (EN, OUTPUT);
  digitalWrite (EN, LOW);

  // Iniciar a serial para aquisição dos dados 
  Serial.begin(9600);
}

void loop () {
  if ( string_complete ){

    uint8_t dir_x   = string_receive[0]; 
    uint8_t ang_x   = string_receive[1];
    uint8_t vel_x   = string_receive[2];
    uint8_t dir_y   = string_receive[3];
    uint8_t ang_y   = string_receive[4];
    uint8_t vel_y   = string_receive[5];
    
    string_receive = ""; 
    string_complete = false;

    int num_steps_x = (int)(ang_x * 8.888);
    int num_steps_y = (int)(ang_y * 8.888);

    bool direc_x = dir_x > 0 ? true : false ; 
    bool direc_y = dir_y > 0 ? true : false ;  

    step( direc_x, num_steps_x, vel_x, direc_y, num_steps_y, vel_y);

    get_sun_position( 2021, 5, 13, 11, 11, 0 );
    
    Serial.print(azimute);
    Serial.print("\t");
    Serial.println(altitude);
  
  }
}
 

void serialEvent(){
  while ( Serial.available()){
    char received = (char) Serial.read();
    if ( received == '~' )
        string_complete = true;
    else 
      string_receive += received; 
  }
}
