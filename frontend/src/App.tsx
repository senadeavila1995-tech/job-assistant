import { useEffect, useMemo, useState } from 'react'
import Swal from 'sweetalert2'
import type { Application, Job, Match } from './types'

function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [source, setSource] = useState('TODAS')
  const [minScore, setMinScore] = useState(60)
  const [applicationFilter, setApplicationFilter] = useState('TODAS')

  async function loadData() {
    try {
      setLoading(true)

      const [
        jobsResponse,
        matchesResponse,
        applicationsResponse,
      ] = await Promise.all([
        fetch('/api/jobs'),
        fetch('/api/matches'),
        fetch('/api/applications'),
      ])

      if (
        !jobsResponse.ok ||
        !matchesResponse.ok ||
        !applicationsResponse.ok
      ) {
        throw new Error('No se pudieron cargar las ofertas')
      }

      const [
        jobsData,
        matchesData,
        applicationsData,
      ] = await Promise.all([
        jobsResponse.json(),
        matchesResponse.json(),
        applicationsResponse.json(),
      ])

      setJobs(jobsData)
      setMatches(matchesData)
      setApplications(applicationsData)
    } catch (error) {
      console.error(error)

      await Swal.fire({
        icon: 'error',
        title: 'Error de conexión',
        text: 'No fue posible conectar con el backend de Job Assistant.',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const jobMap = useMemo(
    () => new Map(jobs.map((job) => [job.id, job])),
    [jobs],
  )

  const appliedJobIds = useMemo(
    () => new Set(applications.map((application) => application.job_id)),
    [applications],
  )

  console.log('JOB ASSISTANT - aplicaciones:', applications)
  console.log('JOB ASSISTANT - IDs aplicados:', [...appliedJobIds])

  const sources = useMemo(
    () => ['TODAS', ...Array.from(new Set(jobs.map((job) => job.source)))],
    [jobs],
  )

  const filteredMatches = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return matches
      .filter((match) => {
        const job = jobMap.get(match.job_id)

        if (!job) return false

        // El backend ya filtra remoto, pero mantenemos esta
        // validación como segunda barrera en el frontend.
        if (!job.remote || !job.is_active) return false

        const matchesScore = match.score >= minScore

        const matchesSource =
          source === 'TODAS' || job.source === source

        const matchesApplication =
          applicationFilter === 'APLICADAS'
            ? appliedJobIds.has(job.id)
            : !appliedJobIds.has(job.id)

        const searchableText = [
          job.title,
          job.company,
          job.location,
          job.description,
          job.skills,
          job.requirements,
          job.keywords,
          ...match.job_skills,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        const matchesSearch =
          !normalizedSearch ||
          searchableText.includes(normalizedSearch)

        return (
          matchesScore &&
          matchesSource &&
          matchesApplication &&
          matchesSearch
        )
      })
      .sort((a, b) => b.score - a.score)
  }, [
    matches,
    jobMap,
    minScore,
    source,
    search,
    applicationFilter,
    appliedJobIds,
  ])

  const recommendedCount = matches.filter(
    (match) => {
      const job = jobMap.get(match.job_id)
      return job?.remote && job?.is_active &&
        match.recommendation === 'RECOMENDADA'
    },
  ).length

  const reviewCount = matches.filter(
    (match) => {
      const job = jobMap.get(match.job_id)
      return job?.remote && job?.is_active &&
        match.recommendation === 'REVISAR'
    },
  ).length

  const appliedCount = applications.filter(
    (application) => jobMap.get(application.job_id)?.remote,
  ).length

  function formatDate(value: string | null) {
    if (!value) return 'No disponible'

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return value
    }

    return date.toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  function scoreClass(score: number) {
    if (score >= 80) return 'score-high'
    if (score >= 60) return 'score-medium'
    return 'score-low'
  }

  function recommendationClass(recommendation: string) {
    if (recommendation === 'RECOMENDADA') {
      return 'badge-recommended'
    }

    if (recommendation === 'REVISAR') {
      return 'badge-review'
    }

    return 'badge-rejected'
  }

  async function openApplication(job: Job) {
    if (!job.url) {
      await Swal.fire({
        icon: 'warning',
        title: 'Oferta sin enlace',
        text: 'Esta oferta todavía no tiene una URL disponible.',
      })
      return
    }

    window.open(job.url, '_blank', 'noopener,noreferrer')
  }

  async function showJobDetails(
    job: Job,
    match: Match,
    applied: boolean,
  ) {
    const matchedSkills =
      match.matched_skills.length > 0
        ? match.matched_skills
            .map(
              (skill) =>
                `<span class="badge text-bg-success me-1 mb-1">${skill}</span>`,
            )
            .join('')
        : '<span class="text-muted">Ninguna registrada</span>'

    const missingSkills =
      match.missing_skills.length > 0
        ? match.missing_skills
            .map(
              (skill) =>
                `<span class="badge text-bg-warning me-1 mb-1">${skill}</span>`,
            )
            .join('')
        : '<span class="text-muted">Ninguna</span>'

    await Swal.fire({
      title: job.title,
      width: 850,
      html: `
        <div class="text-start">

          <div class="mb-3">
            <strong>${job.company}</strong>
            <br>
            <small class="text-muted">
              ${job.source}
              ${job.location ? ` · ${job.location}` : ''}
            </small>
          </div>

          <div class="row g-2 mb-3">

            <div class="col-md-4">
              <div class="p-2 bg-light rounded">
                <small class="text-muted d-block">Score</small>
                <strong>${match.score.toFixed(1)}/100</strong>
              </div>
            </div>

            <div class="col-md-4">
              <div class="p-2 bg-light rounded">
                <small class="text-muted d-block">Modalidad</small>
                <strong>100% remoto</strong>
              </div>
            </div>

            <div class="col-md-4">
              <div class="p-2 bg-light rounded">
                <small class="text-muted d-block">Salario</small>
                <strong>${job.salary ?? 'No especificado'}</strong>
              </div>
            </div>

          </div>

          <hr>

          <h6>Información de la oferta</h6>

          <p>
            <strong>Ubicación:</strong>
            ${job.location ?? 'No disponible'}
          </p>

          <p>
            <strong>Contrato:</strong>
            ${job.contract_type ?? 'No especificado'}
          </p>

          <p>
            <strong>Jornada:</strong>
            ${job.workday ?? 'No especificada'}
          </p>

          <p>
            <strong>Experiencia:</strong>
            ${job.experience ?? 'No especificada'}
          </p>

          <p>
            <strong>Educación:</strong>
            ${job.education ?? 'No especificada'}
          </p>

          <p>
            <strong>Publicada:</strong>
            ${formatDate(job.published_at)}
          </p>

          <p>
            <strong>Última actualización detectada:</strong>
            ${formatDate(job.last_seen_at)}
          </p>

          <hr>

          <h6>Descripción</h6>
          <p>${job.description ?? 'No disponible'}</p>

          <h6>Requisitos</h6>
          <p>${job.requirements ?? 'No disponibles'}</p>

          <h6>Habilidades de la oferta</h6>
          <p>${job.skills ?? 'No disponibles'}</p>

          <h6>Palabras clave</h6>
          <p>${job.keywords ?? 'No disponibles'}</p>

          <hr>

          <h6>Coincidencias con tu perfil</h6>
          <div class="mb-2">
            ${matchedSkills}
          </div>

          <h6>Habilidades faltantes</h6>
          <div class="mb-3">
            ${missingSkills}
          </div>

          ${
            applied
              ? `
                <div class="alert alert-success py-2">
                  ✓ Ya registraste una aplicación para esta oferta.
                </div>
              `
              : ''
          }

        </div>
      `,
      confirmButtonText: 'Cerrar',
    })
  }

  async function markAsApplied(job: Job) {
    if (appliedJobIds.has(job.id)) {
      await Swal.fire({
        icon: 'info',
        title: 'Oferta ya registrada',
        text: 'Esta oferta ya está marcada como aplicada.',
      })
      return
    }

    const result = await Swal.fire({
      icon: 'question',
      title: '¿Ya aplicaste?',
      text: `Confirma que ya enviaste tu postulación para "${job.title}".`,
      showCancelButton: true,
      confirmButtonText: 'Sí, ya apliqué',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#198754',
    })

    if (!result.isConfirmed) return

    try {
      const response = await fetch(
        `/api/applications/${job.id}`,
        {
          method: 'POST',
        },
      )

      if (!response.ok) {
        throw new Error('No se pudo registrar la aplicación')
      }

      await loadData()

      await Swal.fire({
        icon: 'success',
        title: 'Aplicación registrada',
        text: 'Job Assistant recordará que ya aplicaste a esta oferta.',
      })
    } catch (error) {
      console.error(error)

      await Swal.fire({
        icon: 'error',
        title: 'No se pudo registrar',
        text: 'Ocurrió un error al guardar la aplicación.',
      })
    }
  }

  async function unmarkAsApplied(job: Job) {
    const result = await Swal.fire({
      icon: 'warning',
      title: '¿Quitar aplicación?',
      text: 'La oferta volverá a aparecer como pendiente.',
      showCancelButton: true,
      confirmButtonText: 'Sí, quitar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#dc3545',
    })

    if (!result.isConfirmed) return

    try {
      const response = await fetch(
        `/api/applications/${job.id}`,
        {
          method: 'DELETE',
        },
      )

      if (!response.ok) {
        throw new Error('No se pudo eliminar la aplicación')
      }

      await loadData()

      await Swal.fire({
        icon: 'success',
        title: 'Registro actualizado',
        text: 'La oferta vuelve a estar pendiente.',
      })
    } catch (error) {
      console.error(error)

      await Swal.fire({
        icon: 'error',
        title: 'No se pudo actualizar',
        text: 'Ocurrió un error al actualizar la aplicación.',
      })
    }
  }

  if (loading) {
    return (
      <div className="app-shell d-flex align-items-center justify-content-center">
        <div className="text-center">
          <div
            className="spinner-border text-primary mb-3"
            role="status"
          />
          <h5>Cargando ofertas...</h5>
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">

      <nav className="navbar dashboard-navbar navbar-dark">
        <div className="container-fluid px-4">
          <span className="navbar-brand fw-bold">
            Job Assistant
          </span>

          <span className="text-white-50 small">
            Ofertas 100% remotas
          </span>
        </div>
      </nav>

      <main className="container-fluid px-3 px-lg-4 py-4">

        <section className="hero-section mb-4">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
              <h1 className="h3 fw-bold mb-1">
                Ofertas laborales
              </h1>

              <p className="text-muted mb-0">
                Oportunidades remotas ordenadas por compatibilidad con tu perfil.
              </p>
            </div>

            <button
              className="btn btn-outline-primary"
              onClick={loadData}
            >
              ↻ Actualizar
            </button>
          </div>
        </section>

        <section className="stats-grid">

          <div className="stat-card">
            <span className="stat-label">Ofertas remotas</span>
            <strong>{jobs.length}</strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">Recomendadas</span>
            <strong>{recommendedCount}</strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">Para revisar</span>
            <strong>{reviewCount}</strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">Ya aplicaste</span>
            <strong>{appliedCount}</strong>
          </div>

        </section>

        <section className="filter-card mb-4">

          <div className="row g-3 align-items-end filters-grid">

            <div className="col-12 col-lg-5">
              <label className="form-label fw-semibold">
                Buscar
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Cargo, empresa, tecnología..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
              />
            </div>

            <div className="col-6 col-lg-2">
              <label className="form-label fw-semibold">
                Fuente
              </label>

              <select
                className="form-select"
                value={source}
                onChange={(event) =>
                  setSource(event.target.value)
                }
              >
                {sources.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div className="col-6 col-lg-2">
              <label className="form-label fw-semibold">
                Score mínimo
              </label>

              <select
                className="form-select"
                value={minScore}
                onChange={(event) =>
                  setMinScore(Number(event.target.value))
                }
              >
                <option value={0}>Todos</option>
                <option value={60}>60+</option>
                <option value={70}>70+</option>
                <option value={80}>80+</option>
                <option value={90}>90+</option>
              </select>
            </div>

            <div className="col-12 col-lg-3">
              <label className="form-label fw-semibold">
                Aplicación
              </label>

              <select
                className="form-select"
                value={applicationFilter}
                onChange={(event) =>
                  setApplicationFilter(event.target.value)
                }
              >
                <option value="TODAS">Todas</option>
                <option value="PENDIENTES">Pendientes</option>
                <option value="APLICADAS">Aplicadas</option>
              </select>
            </div>

          </div>

        </section>

        {filteredMatches.length === 0 ? (
          <div className="empty-state">
            <h5>No hay ofertas que coincidan</h5>
            <p className="text-muted mb-0">
              Prueba cambiando la búsqueda o el score mínimo.
            </p>
          </div>
        ) : (
          <section className="job-grid">

            {filteredMatches.map((match) => {
              const job = jobMap.get(match.job_id)

              if (!job) return null

              const applied = appliedJobIds.has(job.id)

              return (
                <div key={job.id}>
                  <article className="job-card">

                    <div className="job-card-header">

                      <div className="flex-grow-1 min-w-0">

                        <div className="job-card-badges mb-2">

                          <span className="badge text-bg-success">
                            REMOTO
                          </span>

                          <span
                            className={`badge ${recommendationClass(
                              match.recommendation,
                            )}`}
                          >
                            {match.recommendation}
                          </span>

                          {applied && (
                            <span className="badge text-bg-dark">
                              ✓ APLICADA
                            </span>
                          )}

                        </div>

                        <div className="job-title">
                          {job.title}
                        </div>

                        <div className="company-name">
                          {job.company}
                        </div>

                      </div>

                      <div
                        className={`score-circle ${scoreClass(
                          match.score,
                        )}`}
                      >
                        <strong>
                          {match.score.toFixed(1)}
                        </strong>

                        <small>
                          MATCH
                        </small>
                      </div>

                    </div>

                    <div className="job-summary">

                      <div className="summary-item">
                        <span>Ubicación</span>
                        <strong>
                          {job.location ?? 'Colombia'}
                        </strong>
                      </div>

                      <div className="summary-item">
                        <span>Salario</span>
                        <strong>
                          {job.salary ?? 'No especificado'}
                        </strong>
                      </div>

                      <div className="summary-item">
                        <span>Jornada</span>
                        <strong>
                          {job.workday ?? 'No especificada'}
                        </strong>
                      </div>

                      <div className="summary-item">
                        <span>Experiencia</span>
                        <strong>
                          {job.experience ?? 'No especificada'}
                        </strong>
                      </div>

                    </div>

                    <div className="match-summary">

                      <div>
                        <span>Skills</span>
                        <strong>
                          {match.skill_score.toFixed(0)}%
                        </strong>
                      </div>

                      <div>
                        <span>Cargo</span>
                        <strong>
                          {match.role_score.toFixed(0)}%
                        </strong>
                      </div>

                      <div>
                        <span>Remoto</span>
                        <strong>
                          {match.remote_score.toFixed(0)}%
                        </strong>
                      </div>

                    </div>

                    <div className="skills-section">

                      <div className="skills-title">
                        Tecnologías
                      </div>

                      <div>
                        {match.matched_skills
                          .slice(0, 5)
                          .map((skill) => (
                            <span
                              className="skill skill-matched me-1 mb-1"
                              key={skill}
                            >
                              {skill}
                            </span>
                          ))}

                        {match.matched_skills.length > 5 && (
                          <span className="skill skill-more">
                            +{match.matched_skills.length - 5}
                          </span>
                        )}
                      </div>

                    </div>

                    <div className="job-date mt-2">
                      Publicada:{' '}
                      {formatDate(job.published_at)}
                    </div>

                    <div className="job-actions">

                      <button
                        className="btn btn-outline-secondary btn-sm"
                        onClick={() =>
                          showJobDetails(
                            job,
                            match,
                            applied,
                          )
                        }
                      >
                        Ver detalles
                      </button>

                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() =>
                          openApplication(job)
                        }
                      >
                        ↗ Aplicar
                      </button>

                    </div>

                    <div className="mt-2">

                      {applied ? (
                        <button
                          className="btn btn-outline-danger btn-sm w-100"
                          onClick={() =>
                            unmarkAsApplied(job)
                          }
                        >
                          Quitar marca de aplicación
                        </button>
                      ) : (
                        <button
                          className="btn btn-outline-success btn-sm w-100"
                          onClick={() =>
                            markAsApplied(job)
                          }
                        >
                          ✓ Ya apliqué a esta oferta
                        </button>
                      )}

                    </div>

                  </article>
                </div>
              )
            })}

          </section>
        )}

      </main>
    </div>
  )
}

export default App
