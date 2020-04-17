export class ErrorMessageCreator {
  createStringMessage(error: any): string {
    let result = '';
    if (error.error) {
      if (typeof error.error === 'string' || error.error instanceof String) {
        result = error.error;
      } else {
        Object.keys(error.error).forEach(e => {
          result += `${e} -> ${error.error[e]}
          `;
        });
      }
    } else {
      result = 'undefined error';
    }
    return result;
  }
}
