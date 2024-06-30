import { TestBed } from '@angular/core/testing';

import { FileUploadServiceService } from './file-upload-service.service';

describe('FileUploadServiceService', () => {
  let service: FileUploadServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FileUploadServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
