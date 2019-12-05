import { HttpErrorResponse } from '@angular/common/http';

export class ErrorMessageCreator {
  createStringMessage(error: any): string {
    let result = '';
    if (error.error) {
      Object.keys(error.error).forEach(e => {
        result = `${e} -> ${error.error[e]}
        `;
      });
      // error.error.forEach(message => {
      //   message = `Message: ${message[0]}
      //   `;
      // });
    } else {
      result = 'undefined error';
    }
    return result;
  }
}
