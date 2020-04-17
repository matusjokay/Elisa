import { Period } from 'src/app/models/period.model';
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'parsePeriods'
})
export class ParsePeriodsPipe implements PipeTransform {

  transform(periods: Period[], ids: number[]): any {
    const values = [];
    periods.forEach(period => {
      if (!period.name.includes('- ') && !ids.includes(period.id)) {
        values.push(period);
      }
    });
    return values;
  }

}
