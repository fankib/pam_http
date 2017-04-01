#define PAM_SM_AUTH

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

#include <security/pam_modules.h>

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv);
PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv);
// PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv);
// PAM_EXTERN int pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc, const char **argv);
// PAM_EXTERN int pam_sm_open_session(pam_handle_t *pamh, int flags, int argc, const char **argv);
// PAM_EXTERN int pam_sm_close_session(pam_handle_t *pamh, int flags, int argc, const char **argv);

typedef unsigned long ulong;

PAM_EXTERN
int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv){
	const char* username;
	if (pam_get_user(pamh, &username, NULL) != PAM_SUCCESS) {
		fprintf(stderr, "[pam_http] %s", "cannot determine user name");
		return PAM_USER_UNKNOWN;
	}
	fprintf(stderr, "[pam_http] check credentials for: %s\n", username);
	
	char filename[] = "/tmp/http_success";
	// TODO: read filename from argv
	
	// read file
	FILE *fp;
	char *line = NULL;
    size_t len = 0;
    ssize_t read;

	int success = 0;

	fp = fopen(filename,"r"); // read mode

	if( fp == NULL ) {
		fprintf(stderr, "[pam_http] file not found: %s\n", filename);
		return PAM_CRED_UNAVAIL;
	}

	while( (read = getline(&line, &len, fp)) != EOF ){		
		// printf("parse line %s", line);		
		char *token;
		token = strtok(line, ";");
		if(token){
			// printf("token: %s", token);
			if (strncmp(username, token, strlen(username)) == 0){
				// printf(" match!!\n");				
				token = strtok(NULL, ";");
				
				long timestamp;
				long then;
				long time_left;
				long delta;
				long max_time = 10; // TODO: get from argv
				
				timestamp = (long) time(NULL);
				char *p;
				then = strtoul(token, &p, 0);
				time_left = max_time - (timestamp - then);
				if ( time_left < 0 ){
					time_left = 0;
				}
				printf("[pam_http] time left %li\n", time_left);
				
				if ( time_left > 0 ){ 
					success = 1;
				}
			}
		}		
			
		fclose(fp);
		
		if (success){				
			fp = fopen(filename, "w");
			fwrite("\n", 1, 1, fp);
			fclose(fp);			
			return PAM_SUCCESS;
		}		
		return PAM_AUTH_ERR;
	}

	fclose(fp);	
	// printf("no match.. \n");
	return PAM_AUTH_ERR;
}

PAM_EXTERN
int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv){
	return PAM_SUCCESS;
}

#ifdef PAM_STATIC

struct pam_module _pam_tunnels_modstruct = {
	"pam_http",
	pam_sm_authenticate,
	pam_sm_setcred,
	NULL,
	NULL,
	NULL,
	NULL
};

#endif

/*
PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv){
	fprintf(stderr, "%s", "acct_mgmt");
	return PAM_AUTH_ERR;
}

PAM_EXTERN int pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc, const char **argv){
	fprintf(stderr, "%s", "change authentication token");
	return PAM_AUTH_ERR;
}

PAM_EXTERN int pam_sm_open_session(pam_handle_t *pamh, int flags, int argc, const char **argv){
	fprintf(stderr, "%s", "open_session");
	return PAM_AUTH_ERR;
}

PAM_EXTERN int pam_sm_close_session(pam_handle_t *pamh, int flags, int argc, const char **argv){
	fprintf(stderr, "%s", "close_session");
	return PAM_AUTH_ERR;
}
*/


