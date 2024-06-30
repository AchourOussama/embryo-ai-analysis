import { TestBed } from '@angular/core/testing';

import { EmbryonService } from './embryon.service';

describe('EmbryonService', () => {
  let service: EmbryonService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EmbryonService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
