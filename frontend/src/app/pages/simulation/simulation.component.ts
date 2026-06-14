import { DatePipe, KeyValuePipe, PercentPipe, UpperCasePipe } from '@angular/common';
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
  imports: [DatePipe, KeyValuePipe, PercentPipe, UpperCasePipe, RouterLink],
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
  readonly timeline = toSignal(this.worldCupService.getRoadToTheTrophyTimeline());
  readonly referenceOdds = toSignal(this.worldCupService.getMatchReferenceOddsV2231());
  readonly selectedStateId = signal('current');
  readonly comparisonSide = signal<'before' | 'after'>('after');
  readonly comparisonEnabled = signal(false);
  readonly selectedGroup = signal<string | null>(null);
  readonly selectedRound = signal('all');
  readonly selectedStatus = signal('all');
  readonly selectedTeam = signal<string | null>(null);
  readonly selectedMatchId = signal<string | null>(null);
  readonly mode = signal<'overview' | 'team_focus' | 'group_focus' | 'round_focus'>('overview');
  readonly zoomLevel = signal(0.42);

  readonly worldWidth = 4300;
  readonly worldHeight = 3040;
  readonly roundX = [1050, 1710, 2370, 3030, 3690];

  readonly selectedStateIndex = computed(() => {
    const states = this.timeline()?.states ?? [];
    const index = states.findIndex((state: any) => state.state_id === this.selectedStateId());
    return index < 0 ? Math.max(0, states.length - 1) : index;
  });
  readonly selectedTimelineDiff = computed(() => this.timeline()?.diffs?.find((diff: any) => diff.to_state_id === this.selectedStateId()) ?? null);
  readonly activeState = computed(() => {
    const timeline = this.timeline();
    if (!timeline?.states?.length) return null;
    const index = this.selectedStateIndex();
    const activeIndex = this.comparisonEnabled() && this.comparisonSide() === 'before' ? Math.max(0, index - 1) : index;
    return timeline.states[activeIndex];
  });
  readonly activeData = computed(() => this.activeState()?.scenario ?? this.vm());
  readonly previousData = computed(() => {
    const states = this.timeline()?.states ?? [];
    return states[Math.max(0, this.selectedStateIndex() - 1)]?.scenario ?? null;
  });
  readonly activeGroup = computed(() => this.activeData()?.groups.find((group: any) => group.group === this.selectedGroup()));
  readonly selectedTeamPath = computed(() => this.activeData()?.team_paths[this.selectedTeam() ?? ''] ?? null);
  readonly selectedMatch = computed(() => {
    const data = this.activeData();
    if (!data) return null;
    return [
      ...data.groups.flatMap((group: any) => group.matches),
      ...data.rounds.flatMap((round: any) => round.matches),
      data.third_place,
    ].find((match: any) => match.match_id === this.selectedMatchId());
  });
  readonly selectedReferenceOdds = computed(() => this.referenceOdds()?.fixtures?.find((row: any) => row.match_id === this.selectedMatchId()) ?? null);

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
    const index = this.activeData()?.groups.findIndex((group: any) => group.group === code) ?? 0;
    const position = this.groupPosition(index);
    this.moveTo(position.x + 180, position.y + 215, 0.9);
  }

  focusRound(key: string): void {
    this.selectedRound.set(key);
    this.mode.set('round_focus');
    const index = this.activeData()?.rounds.findIndex((round: any) => round.key === key) ?? 0;
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

  selectTimelineState(stateId: string): void {
    this.selectedStateId.set(stateId);
    this.comparisonSide.set('after');
  }

  moveTimeline(delta: number): void {
    const states = this.timeline()?.states ?? [];
    const index = Math.max(0, Math.min(states.length - 1, this.selectedStateIndex() + delta));
    if (states[index]) this.selectTimelineState(states[index].state_id);
  }

  isGroupChanged(code: string): boolean {
    return this.selectedTimelineDiff()?.group_changes?.includes(code) ?? false;
  }

  isKnockoutChanged(matchId: string): boolean {
    return this.selectedTimelineDiff()?.bracket_changes?.some((row: any) => row.match_id === matchId) ?? false;
  }

  isSelectedTeamMatch(matchId: string): boolean {
    return this.selectedTeamPath()?.knockout_path?.some((step: any) => step.match_id === matchId) ?? false;
  }

  teamPathSegments(path: any): string[] {
    const data = this.activeData();
    if (!data || !path?.knockout_path?.length) return [];
    const segments: string[] = [];
    const groupIndex = data.groups.findIndex((group: any) => group.group === path.group);
    const firstId = path.knockout_path[0].match_id;
    const firstIndex = this.roundMatchIndex(data.rounds[0], firstId);
    if (groupIndex >= 0 && firstIndex >= 0) segments.push(this.groupPath(groupIndex, firstIndex));
    for (let index = 0; index < path.knockout_path.length - 1; index++) {
      const currentId = path.knockout_path[index].match_id;
      const nextId = path.knockout_path[index + 1].match_id;
      const roundIndex = data.rounds.findIndex((round: any) => round.matches.some((match: any) => match.match_id === currentId));
      if (roundIndex < 0 || roundIndex >= data.rounds.length - 1) continue;
      const currentIndex = this.roundMatchIndex(data.rounds[roundIndex], currentId);
      const nextIndex = this.roundMatchIndex(data.rounds[roundIndex + 1], nextId);
      if (currentIndex >= 0 && nextIndex >= 0) segments.push(this.knockoutPath(roundIndex, currentIndex, data.rounds[roundIndex].matches.length, nextIndex, data.rounds[roundIndex + 1].matches.length));
    }
    return segments;
  }

  stableId(value: string): string {
    return value.replace(/[^a-zA-Z0-9_-]/g, '-');
  }

  teamKey(value: string | number | symbol): string {
    return String(value);
  }

  isTeamImpacted(team: string): boolean {
    return this.selectedTimelineDiff()?.qualification_changes?.some((row: any) => row.team === team) ?? false;
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
