import { DatePipe, PercentPipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { select, Selection } from 'd3-selection';
import 'd3-transition';
import { zoom, ZoomBehavior, zoomIdentity } from 'd3-zoom';
import { WorldCupService } from '../../services/worldcup.service';

@Component({
  selector: 'app-simulation',
  imports: [DatePipe, PercentPipe, RouterLink],
  templateUrl: './simulation.component.html',
  styleUrl: './simulation.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulationComponent {
  private readonly worldCupService = inject(WorldCupService);
  private zoomBehavior?: ZoomBehavior<HTMLElement, unknown>;
  private viewportSelection?: Selection<HTMLElement, unknown, null, undefined>;

  atlasViewport?: ElementRef<HTMLElement>;
  atlasWorld?: ElementRef<HTMLElement>;
  @ViewChild('atlasViewport') set viewportRef(value: ElementRef<HTMLElement> | undefined) {
    this.atlasViewport = value;
    queueMicrotask(() => this.initializeAtlas());
  }
  @ViewChild('atlasWorld') set worldRef(value: ElementRef<HTMLElement> | undefined) {
    this.atlasWorld = value;
    queueMicrotask(() => this.initializeAtlas());
  }

  readonly vm = toSignal(this.worldCupService.getRoadToTheTrophyEngine());
  readonly selectedGroup = signal<string | null>(null);
  readonly selectedRound = signal('all');
  readonly selectedStatus = signal('all');
  readonly selectedTeam = signal<string | null>(null);
  readonly selectedMatchId = signal<string | null>(null);
  readonly showEvolution = signal(false);
  readonly mode = signal<'overview' | 'team_focus' | 'group_focus' | 'round_focus'>('overview');
  readonly zoomLevel = signal(0.42);

  readonly worldWidth = 4300;
  readonly worldHeight = 3040;
  readonly roundX = [1050, 1710, 2370, 3030, 3690];

  readonly activeGroup = computed(() => this.vm()?.groups.find((group: any) => group.group === this.selectedGroup()));
  readonly selectedTeamPath = computed(() => this.vm()?.team_paths[this.selectedTeam() ?? ''] ?? null);
  readonly selectedMatch = computed(() => {
    const data = this.vm();
    if (!data) return null;
    return [
      ...data.groups.flatMap((group: any) => group.matches),
      ...data.rounds.flatMap((round: any) => round.matches),
      data.third_place,
    ].find((match: any) => match.match_id === this.selectedMatchId());
  });

  private initializeAtlas(): void {
    const viewport = this.atlasViewport?.nativeElement;
    const world = this.atlasWorld?.nativeElement;
    if (!viewport || !world || this.zoomBehavior) return;
    this.viewportSelection = select(viewport);
    this.zoomBehavior = zoom<HTMLElement, unknown>()
      .scaleExtent([0.22, 1.35])
      .translateExtent([[-300, -300], [this.worldWidth + 300, this.worldHeight + 300]])
      .on('zoom', (event) => {
        world.style.transform = `translate(${event.transform.x}px, ${event.transform.y}px) scale(${event.transform.k})`;
        this.zoomLevel.set(event.transform.k);
      });
    this.viewportSelection.call(this.zoomBehavior);
    this.fitOverview();
  }

  groupPosition(index: number): { x: number; y: number } {
    return { x: 50 + (index % 2) * 430, y: 80 + Math.floor(index / 2) * 490 };
  }

  matchPosition(roundIndex: number, matchIndex: number, count: number): { x: number; y: number } {
    return { x: this.roundX[roundIndex], y: ((this.worldHeight - 160) / count) * (matchIndex + 0.5) };
  }

  knockoutPath(roundIndex: number, matchIndex: number, count: number, nextIndex: number, nextCount: number): string {
    const source = this.matchPosition(roundIndex, matchIndex, count);
    const target = this.matchPosition(roundIndex + 1, nextIndex, nextCount);
    return this.curve(source.x + 330, source.y, target.x, target.y);
  }

  roundMatchIndex(round: any, matchId: string): number {
    return round.matches.findIndex((match: any) => match.match_id === matchId);
  }

  groupPath(groupIndex: number, targetIndex: number): string {
    const source = this.groupPosition(groupIndex);
    const target = this.matchPosition(0, targetIndex, 16);
    return this.curve(source.x + 400, source.y + 235, target.x, target.y);
  }

  private curve(x1: number, y1: number, x2: number, y2: number): string {
    const middle = (x1 + x2) / 2;
    return `M ${x1} ${y1} C ${middle} ${y1}, ${middle} ${y2}, ${x2} ${y2}`;
  }

  selectTeam(team: string): void {
    this.selectedTeam.set(team);
    this.selectedMatchId.set(null);
    this.mode.set('team_focus');
  }

  selectMatch(match: any): void {
    this.selectedMatchId.set(match.match_id);
  }

  focusGroup(code: string): void {
    this.selectedGroup.set(code);
    this.selectedTeam.set(null);
    this.mode.set('group_focus');
    const index = this.vm()?.groups.findIndex((group: any) => group.group === code) ?? 0;
    const position = this.groupPosition(index);
    this.moveTo(position.x + 180, position.y + 215, 0.9);
  }

  focusRound(key: string): void {
    this.selectedRound.set(key);
    this.mode.set('round_focus');
    const index = this.vm()?.rounds.findIndex((round: any) => round.key === key) ?? 0;
    this.moveTo(this.roundX[index] + 160, this.worldHeight / 2, 0.45);
  }

  isTeamHighlighted(team: string): boolean {
    return this.selectedTeam() === team;
  }

  isMatchHighlighted(match: any): boolean {
    const team = this.selectedTeam();
    return (
      (!!team && team === match.home_team) ||
      (!!team && team === match.away_team) ||
      (!!team && team === match.team_a) ||
      (!!team && team === match.team_b)
    );
  }

  isMatchVisible(match: any, roundKey?: string): boolean {
    const status = this.selectedStatus();
    const round = this.selectedRound();
    const matchesStatus = status === 'all' || match.display_status === status || match.status === status;
    return matchesStatus && (round === 'all' || !roundKey || round === roundKey);
  }

  fitOverview(): void {
    const viewport = this.atlasViewport?.nativeElement;
    if (!viewport || !this.viewportSelection || !this.zoomBehavior) return;
    const scale = Math.min((viewport.clientWidth - 40) / this.worldWidth, (viewport.clientHeight - 40) / this.worldHeight);
    const x = (viewport.clientWidth - this.worldWidth * scale) / 2;
    const y = (viewport.clientHeight - this.worldHeight * scale) / 2;
    this.viewportSelection.transition().duration(550).call(this.zoomBehavior.transform, zoomIdentity.translate(x, y).scale(scale));
    this.mode.set('overview');
  }

  zoomBy(factor: number): void {
    if (this.viewportSelection && this.zoomBehavior) {
      this.viewportSelection.transition().duration(220).call(this.zoomBehavior.scaleBy, factor);
    }
  }

  private moveTo(worldX: number, worldY: number, scale: number): void {
    const viewport = this.atlasViewport?.nativeElement;
    if (!viewport || !this.viewportSelection || !this.zoomBehavior) return;
    const transform = zoomIdentity
      .translate(viewport.clientWidth / 2 - worldX * scale, viewport.clientHeight / 2 - worldY * scale)
      .scale(scale);
    this.viewportSelection.transition().duration(650).call(this.zoomBehavior.transform, transform);
  }

  reset(): void {
    this.selectedGroup.set(null);
    this.selectedRound.set('all');
    this.selectedStatus.set('all');
    this.selectedTeam.set(null);
    this.selectedMatchId.set(null);
    this.fitOverview();
  }
}
