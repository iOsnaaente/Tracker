/// CRIAÇÃO DAS STRUCTS 
struct STTime {
  int    year   , month  , day ;
  int    hour   , minute ;
  double second ;
};

struct STPosition {
  double julianDay       , tJD, tJC, tJC2, UT ;
  double longitude       , distance           ;
  double obliquity       ,cosObliquity        , nutationLon    ;
  double rightAscension  ,declination         , hourAngle,agst ;
  double altitude        , altitudeRefract    , azimuthRefract ;
  double hourAngleRefract, declinationRefract ;
};

struct STLocation {
  double longitude, latitude   ;
  double sinLat   , cosLat     ;
  double pressure , temperature;
};

// MACRODEFINIÇÕES
# define X_DIR  5  // X -axis stepper motor direction control
# define Y_DIR  6  // y -axis stepper motor direction control
# define X_STP  2  // x -axis stepper control
# define Y_STP  3  // y -axis stepper control
# define EN     8  // stepper motor enable , active low


// IMPORTAÇÕES 
#include <RTClib.h>
#include <Wire.h>


// OBJETOS 
RTC_DS3231 Clock; 
DateTime   Date;


// PRECALL DE FUNÇÕES 
void SolTrack(struct STTime time, struct STLocation location, struct STPosition *position,  int useDegrees, int useNorthEqualsZero, int computeRefrEquatorial, int computeDistance);
void get_sun_position(int year, int month, int day, int hour, int minute, double second);
void printHour();

// INSTANCIAMENTO DAS STRUCTS 
struct STLocation loc  ; 
struct STPosition pos  ;
struct STTime     time ; 


// VARIÁVEIS PARA USO 
String string_receive        = ""    ;  
bool   string_complete       = false ; 
int    useDegrees            = true  ;         
int    useNorthEqualsZero    = true  ;     
int    computeRefrEquatorial = false ;  
int    computeDistance       = false ;        
float  azimute; 
float  altitude; 

float pos_gir = 0 ;
float pos_ele = 0 ; 

float ang_gir = 0 ;
float ang_ele = 0 ;

float deltaAzi;
float deltaAlt;

int num_steps_gir;
int num_steps_ele;

int vel_gir = 100;
int vel_ele = 100;

bool dir_gir = 0 ;
bool dir_ele = 0 ;


void setup () {
  Serial.begin(9600);
  Wire.begin();

  Clock.adjust( DateTime( F(__DATE__), F(__TIME__) ) );   
  
  pinMode (X_DIR, OUTPUT); pinMode (X_STP, OUTPUT);
  pinMode (Y_DIR, OUTPUT); pinMode (Y_STP, OUTPUT);
  pinMode (EN, OUTPUT);

  digitalWrite (EN, LOW);
  
  loc.latitude    = -29.16530765942215 ;    // Latitude 
  loc.longitude   = -54.89831672609559 ;    // Longitude 
  
  loc.pressure    = 101.0 ;                          // Pressão atmosférica em Kpa
  loc.temperature = 273.5 + Clock.getTemperature(); // Temperatura 273.1 + ºC = K 

}

void loop () {
    /*
    uint8_t dir_x   = string_receive[0]; 
    uint8_t ang_x   = string_receive[1];
    uint8_t vel_x   = string_receive[2];
    uint8_t dir_y   = string_receive[3];
    uint8_t ang_y   = string_receive[4];
    uint8_t vel_y   = string_receive[5];
    */
    
    //string_receive = ""; 
    //string_complete = false;

    Date = Clock.now(); 
    
    int year   =  Date.year();  
    int month  =  Date.month();
    int day    =  Date.day(); 
    int hour   =  Date.hour()+3;
    int minute =  Date.minute();
    int second =  Date.second();

    int azi, alt; 

    azi = azimute;
    alt = altitude; 
    
    get_sun_position( year, month, day, hour, minute, second );

    deltaAzi = azimute - azi;
    deltaAlt = altitude - alt;

    pos_gir += deltaAzi;
    pos_ele += deltaAlt; 

    num_steps_gir = abs( (int)(deltaAzi * 8.888) ) ;
    num_steps_ele = abs( (int)(deltaAlt * 8.888) ) ;

    dir_gir = deltaAzi > 0 ? true : false ; 
    dir_ele = deltaAlt > 0 ? true : false ;  

    step( dir_gir, num_steps_gir, vel_gir, dir_ele, num_steps_ele, vel_ele);
        
    printData(); 
    delay(60000); 
}


// FUNÇÕES 
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

 
void printData(){
  Serial.print( Date.year() ); 
  Serial.print("/ "); 
  Serial.print( Date.month() );
  Serial.print("/ "); 
  Serial.print( Date.day() );
  Serial.print("\t\t"); 
  Serial.print( Date.hour() );
  Serial.print(":"); 
  Serial.print( Date.minute() );
  Serial.print(":"); 
  Serial.println( Date.second() ); 

  Serial.print("Altitude: ");
  Serial.print(altitude);
  Serial.print("\t\tAzimute: ");
  Serial.print(azimute);
  Serial.print("\t\tTemperatura: ");
  Serial.println(Clock.getTemperature());

  Serial.print("Pos_gir : ");
  Serial.print(pos_gir);
  Serial.print("\tPos_ele: ");
  Serial.println(pos_ele);
  
  Serial.print("Delta_azi : ");
  Serial.print(deltaAzi);
  Serial.print("\tDelta_ele : ");
  Serial.println(deltaAlt);
  
  Serial.print("Num_steps_gir : ");
  Serial.print(num_steps_gir);
  Serial.print("\tNum_steps_ele : ");
  Serial.println(num_steps_ele);

  Serial.println();
  
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
