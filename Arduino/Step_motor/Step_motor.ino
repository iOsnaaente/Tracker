/// CRIAÇÃO DAS STRUCTS
struct STTime {
  int    year   , month  , day ;
  int    hour   , minute ;
  double second ;
};

struct STPosition {
  double julianDay       , tJD, tJC, tJC2, UT ;
  double longitude       , distance           ;
  double obliquity       , cosObliquity       , nutationLon    ;
  double rightAscension  , declination        , hourAngle, agst ;
  double altitude        , altitudeRefract    , azimuthRefract ;
  double hourAngleRefract, declinationRefract ;
};

struct STLocation {
  double longitude, latitude   ;
  double sinLat   , cosLat     ;
  double pressure , temperature;
};


// INSTANCIAMENTO DAS FUNÇÕES NAS ABAS AO LADO
void SolTrack           ( struct STTime time, struct STLocation location, struct STPosition *position,  int useDegrees, int useNorthEqualsZero, int computeRefrEquatorial, int computeDistance);
void get_sun_position   ( int year, int month, int day, int hour, int minute, double second);
void step               ( boolean dir_x, int steps_x, int vel_x, boolean dir_y,  int steps_y, int vel_y );
void pulse              ( byte stepperPin, byte vel );

/// FUNÇÕES DA MEMÓRIA FLASH 
void chipInformation( byte *ID, byte *memoryType, byte *capacity);
void writeOneByte( unsigned int page, byte offset, byte data );
void writePage( unsigned int page, byte *data_buff );
void readPage ( unsigned int page, byte *page_buff );
void printPage( byte *page );
void chipErase( );
void not_busy ( );
void initSPI  ( );

void send_data          ( int seg, int dias, float az, float alt, int p1, int p2 );
void getDateAndTime     ( );
void serialEvent        ( );
void print_data         ( );
void printHour          ( );

// INSTANCIAMENTO DAS STRUCTS
struct STLocation loc  ;
struct STPosition pos  ;
struct STTime     time ;


// MACRODEFINIÇÕES
# define X_DIR  5  // X -axis stepper motor direction control
# define Y_DIR  6  // y -axis stepper motor direction control
# define X_STP  2  // x -axis stepper control
# define Y_STP  3  // y -axis stepper control
# define EN     8  // stepper motor enable , active low


// IMPORTAÇÕES
#include <EEPROM.h>
#include <RTClib.h>
#include <Wire.h>
#include <crc.h>
#include <SPI.h>

 
// OBJETOS
RTC_DS3231 Clock;
DateTime   Date ;
CRC8       CRC  ;



// VARIÁVEIS PARA USO
String string_receive        = ""    ;
bool   string_complete       = false ;


int    useDegrees            = true  ;
int    useNorthEqualsZero    = true  ;
int    computeRefrEquatorial = false ;
int    computeDistance       = false ;

int year, month , day   ;
int hour, minute, second;

float  pos_gir = 0, pos_ele = 0 ;
float  ang_gir = 0, ang_ele = 0 ;
float  azimute    , azi_ant ;
float  altitude   , alt_ant ;
float  deltaAzi   , deltaAlt;

int    totalSegundos = 0  , totalDias     = 0  ;
int    num_steps_gir      , num_steps_ele      ;
int    vel_gir       = 100, vel_ele       = 100;
int    red_gir       = 10 , red_ele       = 10 ;

bool   dir_gir = 0  , dir_ele = 0  ;

uint8_t CRC_send ;


void setup () {
  Serial.begin(9600);
  Wire.begin();
  initSPI(); 

  Clock.adjust( DateTime( F(__DATE__), F(__TIME__) ) );
  pinMode( X_DIR, OUTPUT); pinMode( X_STP, OUTPUT);
  pinMode( Y_DIR, OUTPUT); pinMode( Y_STP, OUTPUT);
  pinMode( EN   , OUTPUT);
  
  digitalWrite (EN, LOW);
  
  loc.latitude    = -29.16530765942215 ;               // Latitude
  loc.longitude   = -54.89831672609559 ;              // Longitude
  loc.pressure    = 101.0 ;                          // Pressão atmosférica em Kpa
  loc.temperature = 273.5 + Clock.getTemperature(); // Temperatura 273.1 + ºC = K
}


void loop () {
  //string_receive = "";
  //string_complete = false;
  
  getDateAndTime();
  azi_ant = azimute;
  alt_ant = altitude;
  
  totalSegundos = hour * 3600 + minute * 60 + second ;
  SolTrack( time, loc, &pos, useDegrees, useNorthEqualsZero, computeRefrEquatorial, computeDistance);

  azimute       = pos.azimuthRefract;
  altitude      = pos.altitudeRefract;
  totalDias     = pos.julianDay;
  
  deltaAzi = azimute  - azi_ant;
  deltaAlt = altitude - alt_ant;

  pos_gir += deltaAzi;
  pos_ele += deltaAlt;

  // ATUAÇÃO DOS MOTORES
  num_steps_gir = abs( (int)(deltaAzi * 8.888 * red_gir ) ) ;
  num_steps_ele = abs( (int)(deltaAlt * 8.888 * red_ele ) ) ;
  dir_gir       = deltaAzi > 0 ? true : false ; 
  dir_ele       = deltaAlt > 0 ? true : false ;
  step( dir_gir, num_steps_gir * 10, vel_gir, dir_ele, num_steps_ele * 10, vel_ele);

  // MENSAGEM A SER PRINTADA -> (DIA, TotSEGUNDOS, AZI, ALT, P1, P2, CRC)
  send_data( totalSegundos, totalDias, azimute, altitude, pos_gir, pos_ele );

  print_data();
  delay(60000);
}


// AQUISIÇÃO DAS INFORMAÇÕES DE DATA E HORA
void getDateAndTime(){
  Date = Clock.now();
  year   =  Date.year();
  month  =  Date.month();
  day    =  Date.day();
  hour   =  Date.hour() + 3;
  minute =  Date.minute();
  second =  Date.second();
  time.year   = year ; time.month  = month ; time.day    = day    ;
  time.hour   = hour ; time.minute = minute; time.second = second ;
}

// PRINTAR AS INFORMAÇÕES PRINCIPAIS 
void print_data() {
  char buff[255]; 
  sprintf( buff, "\n%04d/%02d/%02d \t\t\t%02d:%02d:%02d", Date.year(), Date.month(), Date.day(), Date.hour(), Date.minute(), Date.second());
  Serial.println(buff);
  Serial.print("Altitude:\t\t\t");
  Serial.println(altitude);
  Serial.print("Azimute:\t\t\t");
  Serial.println(azimute);
  Serial.print("Temperatura:\t\t\t");
  Serial.println(Clock.getTemperature());
  Serial.print("Pos_gir:\t\t\t");
  Serial.println(pos_gir);
  Serial.print("Pos_ele: \t\t\t");
  Serial.println(pos_ele);
  Serial.print("Delta_azi:\t\t\t");
  Serial.println(deltaAzi);
  Serial.print("Delta_ele:\t\t\t");
  Serial.println(deltaAlt);
  sprintf(buff, "Numero de passos do Giro:\t%d\nNumero de passo da elevação:\t%d\nDiasJulianos:\t\t\t%d\nTotal de segundos:\t\t%d\n",
  num_steps_gir, num_steps_ele, pos.julianDay, totalSegundos );
  Serial.println(buff);
}
