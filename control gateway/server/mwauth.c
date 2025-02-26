#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>

char** split_string_at(char *str, char delim);

int check_password(char *password_given, char *uname_given){
  int password_good;
  char data_buff[13];
  char line[256];  
  
  password_good = 0;
  
  FILE *f, *f2;
  /* get the salt and the password hash from the password file */
  f = fopen("password", "r");
  
  // Check if the file was opened successfully.
  if (f != NULL) {

      while (fgets(line, sizeof(line), f)) {
          // Print each line to the standard output.
          //printf("%s", line);
          char **bits;
          char *correct_hash, *salt, *correct_uname;
            
          bits = split_string_at(line,'\n');
          bits = split_string_at(bits[0],' ');
          correct_uname = bits[0];
          salt = bits[1];
          correct_hash = bits[2];
          
          /* is it the user we expect? */
          if(strcmp(uname_given,correct_uname) == 0){

            /* concatenate the salt and the given password, and feed it into sha256 */
            strcpy(data_buff,salt);
            strcpy(data_buff+strlen(salt),password_given);
            sprintf(line,"echo %s | sha256sum",data_buff);
            f2 = popen(line,"r");
            fgets(line,100,f2);
            pclose(f2);

            /* pull out the sha256 hash of the data and compare it to the stored hash */
            bits = split_string_at(line,' ');
            if(strcmp(bits[0],correct_hash) == 0){
              password_good=1;
              break;
            }
          }
      }
      // Close the file stream once all lines have been
      // read.
      fclose(f);
  }
  else {
      // Print an error message to the standard error
      // stream if the file cannot be opened.
      fprintf(stderr, "Unable to open file!\n");
  } 

  return password_good;
}

char** split_string_at(char *str, char delim){
  char **str_bits;
  int n_str_bits, str_bits_ind;
  char *con, *base;
  
  n_str_bits = 1;
  for(con = str; *con != 0; con++)
    if(*con == delim)
      n_str_bits++;
  str_bits = malloc((n_str_bits+1)*sizeof(char*));
  str_bits[n_str_bits] = 0;

  base=con=str;
  str_bits_ind=0;
  while(1){
    if ((*con == delim) || (*con == 0)){
      str_bits[str_bits_ind] = malloc(con-base+1);
      strncpy(str_bits[str_bits_ind], base, con-base);
      str_bits[str_bits_ind][con-base]=0;
      if (*con == 0)
	break;
      str_bits_ind++;
      base=con=con+1;   
    }
    else
      con++;
  }

  return str_bits;
}

int main(int argc, char** argv) {

    //return check_password(argv[1], argv[2]);
    printf(check_password(argv[1], argv[2]) ? "1":"0");
}
