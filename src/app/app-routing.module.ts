import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { HomeComponent } from './home/home.component';
import { AnalyseEmbryonComponent } from './analyse-embryon/analyse-embryon.component'
import { LoginComponent } from './login/login.component';
import { ListComponent } from './list/list.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'analyse-embryon', component: AnalyseEmbryonComponent},
  { path: 'list', component: ListComponent } // New route

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
