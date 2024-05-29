import { TestBed } from '@angular/core/testing';

import { EmbryoService } from './embryo.service';

describe('EmbryoService', () => {
  let service: EmbryoService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EmbryoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
