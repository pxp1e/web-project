import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Subject } from '../../models/subject.model';
import { User } from '../../models/user.model';
import { NavbarComponent } from '../../components/navbar/navbar';

@Component({
  selector: 'app-teams',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, NavbarComponent],
  templateUrl: './teams.component.html',
  styleUrls: ['./teams.component.css']
})
export class TeamsComponent implements OnInit {
  teams: any[] = [];
  subjects: Subject[] = [];
  newTeamName = '';
  selectedSubjectId: number | '' = '';
  error = '';
  success = '';
  searchQuery = '';
  searchResults: User[] = [];
  showMembersModal = false;
  selectedTeam: any = null;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadTeams();
    this.loadSubjects();
  }

  loadSubjects(): void {
    this.api.getSubjects().subscribe({
      next: (s) => { this.subjects = s; this.cdr.detectChanges(); },
      error: () => this.error = 'Failed to load subjects'
    });
  }

  loadTeams(): void {
    this.api.getTeams().subscribe({
      next: (t) => { this.teams = t; this.cdr.detectChanges(); },
      error: () => this.error = 'Failed to load teams'
    });
  }

  createTeam(): void {
    if (!this.newTeamName || !this.selectedSubjectId) {
      this.error = 'Please fill team name and select subject';
      return;
    }
    this.api.createTeam(this.newTeamName, Number(this.selectedSubjectId)).subscribe({
      next: (t) => {
        this.teams = [...this.teams, t];
        this.newTeamName = '';
        this.selectedSubjectId = '';
        this.error = '';
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to create team'
    });
  }

  deleteTeam(id: number): void {
  if (!confirm('Are you sure you want to delete this team?')) return;
  this.api.deleteTeam(id).subscribe({
    next: () => {
      this.teams = this.teams.filter(t => t.id !== id);
      this.cdr.detectChanges();
    },
    error: () => this.error = 'Failed to delete team'
  });
}

  isAdmin(team: any): boolean {
    return team.my_role === 'admin';
  }

  openMembers(team: any): void {
    this.selectedTeam = team;
    this.showMembersModal = true;
    this.cdr.detectChanges();
  }

  closeMembers(): void {
    this.showMembersModal = false;
    this.selectedTeam = null;
    this.cdr.detectChanges();
  }

  searchUsers(): void {
    if (this.searchQuery.length < 2) return;
    this.api.searchUsers(this.searchQuery).subscribe({
      next: (users) => { this.searchResults = users; this.cdr.detectChanges(); },
      error: () => this.error = 'Search failed'
    });
  }

  addMember(username: string): void {
    if (!this.selectedTeam) return;
    this.api.addMember(this.selectedTeam.id, username).subscribe({
      next: (team) => {
        this.selectedTeam = team;
        this.loadTeams();
        this.searchQuery = '';
        this.searchResults = [];
        this.success = 'Member added';
        this.cdr.detectChanges();
        setTimeout(() => { this.success = ''; this.cdr.detectChanges(); }, 3000);
      },
      error: () => this.error = 'Failed to add member'
    });
  }

  removeMember(userId: number): void {
    if (!this.selectedTeam) return;
    this.api.removeMember(this.selectedTeam.id, userId).subscribe({
      next: () => {
        this.selectedTeam.memberships =
          this.selectedTeam.memberships.filter((m: any) => m.user.id !== userId);
        this.loadTeams();
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to remove member'
    });
  }
}