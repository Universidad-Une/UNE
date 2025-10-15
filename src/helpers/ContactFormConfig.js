import { programasEducativos } from "@helpers/estructura_educativa.js";

export class FormValidator {
  constructor(formSelector, config = {}) {
    this.form = document.querySelector(formSelector);
    this.config = config;
    this.processedData = null;
    this.validationErrors = {};
    this.commonEmailProviders = [
      "gmail.com",
      "outlook.com",
      "hotmail.com",
      "yahoo.com",
      "icloud.com",
      "live.com",
      "msn.com",
      "protonmail.com",
      "zoho.com",
    ];

    if (!this.form) {
      console.error(`Formulario no encontrado: ${formSelector}`);
      return;
    }

    this.init();
  }

  init() {
    this.setupNivelMapping();
    this.processEducationData();
    this.setupElements();
    this.setupEventListeners();
    this.initializeNivelEducativo();
    this.setupValidationStyles();
  }

  setupNivelMapping() {
    this.nivelMapping = {
      Licenciaturas: {
        key: "licenciaturas",
        nombre: "Licenciatura",
        requiereArea: true,
        requierePrograma: true,
      },
      Secundaria: {
        key: "secundaria",
        nombre: "Secundaria",
        requiereArea: false,
        requierePrograma: true,
      },
      Primaria: {
        key: "primaria",
        nombre: "Primaria",
        requiereArea: false,
        requierePrograma: true,
      },
      Bachillerato: {
        key: "bachillerato",
        nombre: "Bachillerato",
        requiereArea: false,
        requierePrograma: true,
      },
      Especialidades: {
        key: "especialidades",
        nombre: "Especialidad",
        requiereArea: true,
        requierePrograma: true,
      },
      Maestrías: {
        key: "Maestrías",
        nombre: "Maestría",
        requiereArea: true,
        requierePrograma: true,
      },
      Continua: {
        key: "continua",
        nombre: "Educación Continua",
        requiereArea: true,
        requierePrograma: true,
      },
    };
  }

  setupElements() {
    // Encontrar elementos dentro del formulario o en el documento
    this.elements = {
      nivelEducativo:
        this.form.querySelector("#nivel-educativo") ||
        document.getElementById("nivel-educativo"),
      areaContainer:
        this.form.querySelector("#area-container") ||
        document.getElementById("area-container"),
      areaConocimiento:
        this.form.querySelector("#area-conocimiento") ||
        document.getElementById("area-conocimiento"),
      programaContainer:
        this.form.querySelector("#programa-container") ||
        document.getElementById("programa-container"),
      programaInteres:
        this.form.querySelector("#programa-interes") ||
        document.getElementById("programa-interes"),
      plantelInteres:
        this.form.querySelector("#plantel-interes") ||
        document.getElementById("plantel-interes"),
      modalidadContainer:
        this.form.querySelector("#modalidad-container") ||
        document.getElementById("modalidad-container"),
      modalidadOptions:
        this.form.querySelector("#modalidad-options") ||
        document.getElementById("modalidad-options"),
      incorporacionHidden:
        this.form.querySelector("#incorporacion-hidden") ||
        document.getElementById("incorporacion-hidden"),
      apellidosInput:
        this.form.querySelector("#apellidos-input") ||
        document.getElementById("apellidos-input"),
      apellidoPaternoHidden:
        this.form.querySelector("#apellido_p_hidden") ||
        document.getElementById("apellido_p_hidden"),
      apellidoMaternoHidden:
        this.form.querySelector("#apellido_m_hidden") ||
        document.getElementById("apellido_m_hidden"),
      correoInput:
        this.form.querySelector("#correo-input") ||
        document.getElementById("correo-input"),
      emailSuggestions:
        this.form.querySelector("#email-suggestions") ||
        document.getElementById("email-suggestions"),
      nombreInput:
        this.form.querySelector("#nombre-input") ||
        document.getElementById("nombre-input") ||
        this.form.querySelector('input[name="nombre"]'),
      telefonoInput:
        this.form.querySelector("#telefono-input") ||
        document.getElementById("telefono-input") ||
        this.form.querySelector('input[name="telefono"]'),
    };
  }

  // ==========================================
  // FUNCIONES DE VALIDACIÓN
  // ==========================================

  setupValidationStyles() {
    // Crear estilos CSS para validaciones si no existen
    if (!document.getElementById("form-validation-styles")) {
      const style = document.createElement("style");
      style.id = "form-validation-styles";
      style.textContent = `
        .field-error {
          border-color: #ef4444 !important;
          box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
        }
        .field-success {
          border-color: #10b981 !important;
          box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
        }
        .error-message {
          color: #ef4444;
          font-size: 0.875rem;
          margin-top: 0.25rem;
          display: block;
        }
        .success-message {
          color: #10b981;
          font-size: 0.875rem;
          margin-top: 0.25rem;
          display: block;
        }
      `;
      document.head.appendChild(style);
    }
  }

  showFieldError(fieldElement, message) {
    if (!fieldElement) return;

    this.clearFieldValidation(fieldElement);
    fieldElement.classList.add("field-error");

    const errorElement = document.createElement("span");
    errorElement.className = "error-message";
    errorElement.textContent = message;
    errorElement.setAttribute("data-validation", "error");

    fieldElement.parentNode.appendChild(errorElement);
  }

  showFieldSuccess(fieldElement, message = "") {
    if (!fieldElement) return;

    this.clearFieldValidation(fieldElement);
    fieldElement.classList.add("field-success");

    if (message) {
      const successElement = document.createElement("span");
      successElement.className = "success-message";
      successElement.textContent = message;
      successElement.setAttribute("data-validation", "success");
      fieldElement.parentNode.appendChild(successElement);
    }
  }

  clearFieldValidation(fieldElement) {
    if (!fieldElement) return;

    fieldElement.classList.remove("field-error", "field-success");
    const validationMessages =
      fieldElement.parentNode.querySelectorAll("[data-validation]");
    validationMessages.forEach((msg) => msg.remove());
  }

  validateName(value) {
    const trimmed = value.trim();
    if (!trimmed) {
      return { valid: true, message: "" }; // NOMBRE AHORA OPCIONAL
    }
    if (trimmed.length < 2) {
      return {
        valid: false,
        message: "El nombre debe tener al menos 2 caracteres",
      };
    }
    if (!/^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+$/.test(trimmed)) {
      return {
        valid: false,
        message: "El nombre solo puede contener letras y espacios",
      };
    }
    return { valid: true, message: "" };
  }

  validateLastNames(value) {
    const trimmed = value.trim();
    if (!trimmed) {
      return { valid: false, message: "Es necesario minimo un apellido" };
    }
    if (trimmed.length < 2) {
      return {
        valid: false,
        message: "Los apellidos deben tener al menos 2 caracteres",
      };
    }
    if (!/^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+$/.test(trimmed)) {
      return {
        valid: false,
        message: "Los apellidos solo pueden contener letras y espacios",
      };
    }
    return { valid: true, message: "" };
  }

  validateEmail(value) {
    const trimmed = value.trim();
    if (!trimmed) {
      return { valid: true, message: "" }; // Email es opcional
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      return { valid: false, message: "Ingresa un correo electrónico válido" };
    }

    return { valid: true, message: "Correo válido" };
  }

  validatePhone(value) {
    const trimmed = value.trim();
    if (!trimmed) {
      return { valid: false, message: "El teléfono es obligatorio" };
    }

    // Remover espacios, guiones y paréntesis para validar solo números
    const numbersOnly = trimmed.replace(/[\s\-\(\)]/g, "");

    if (!/^\d{10}$/.test(numbersOnly)) {
      return { valid: false, message: "El teléfono debe tener 10 dígitos" };
    }

    return { valid: true, message: "Teléfono válido" };
  }

  validateEducationLevel(value) {
    if (!value) {
      return { valid: false, message: "Selecciona un nivel educativo" };
    }
    return { valid: true, message: "" };
  }

  validateArea(value, nivelEducativo) {
    if (!nivelEducativo || !this.processedData[nivelEducativo]) {
      return { valid: true, message: "" };
    }

    const nivelData = this.processedData[nivelEducativo];
    if (nivelData.requiereArea && !value) {
      return { valid: false, message: "Selecciona un área de conocimiento" };
    }
    return { valid: true, message: "" };
  }

  validateProgram(value, nivelEducativo, areaConocimiento) {
    if (!nivelEducativo || !this.processedData[nivelEducativo]) {
      return { valid: true, message: "" };
    }

    const nivelData = this.processedData[nivelEducativo];

    // Solo requerir programa si:
    // 1. El nivel requiere programa Y
    // 2. Si requiere área, debe haber área seleccionada OR si no requiere área
    if (nivelData.requierePrograma) {
      if (nivelData.requiereArea && !areaConocimiento) {
        // Si requiere área pero no hay área seleccionada, no validar programa aún
        return { valid: true, message: "" };
      }

      if (!value) {
        return { valid: false, message: "Selecciona un programa de interés" };
      }
    }

    return { valid: true, message: "" };
  }

  validateCampus(value) {
    if (!value) {
      return { valid: false, message: "Selecciona un plantel de interés" };
    }
    return { valid: true, message: "" };
  }

  validateModality() {
    const modalidadHidden = this.form.querySelector(
      'input[name="modalidad"][type="hidden"]'
    );
    const modalidadRadio = this.form.querySelector(
      'input[name="modalidad"]:checked'
    );

    if (!modalidadHidden && !modalidadRadio) {
      return { valid: false, message: "Selecciona una modalidad" };
    }
    return { valid: true, message: "" };
  }

  setupRealTimeValidation() {
    const {
      nombreInput,
      apellidosInput,
      correoInput,
      telefonoInput,
      nivelEducativo,
      areaConocimiento,
      programaInteres,
      plantelInteres,
    } = this.elements;

    // Validación en tiempo real para nombre
    if (nombreInput) {
      nombreInput.addEventListener("blur", () => {
        const validation = this.validateName(nombreInput.value);
        if (validation.valid) {
          this.showFieldSuccess(nombreInput);
        } else {
          this.showFieldError(nombreInput, validation.message);
        }
      });

      nombreInput.addEventListener("input", () => {
        if (nombreInput.classList.contains("field-error")) {
          const validation = this.validateName(nombreInput.value);
          if (validation.valid) {
            this.showFieldSuccess(nombreInput);
          }
        }
      });
    }

    // Validación en tiempo real para apellidos
    if (apellidosInput) {
      apellidosInput.addEventListener("blur", () => {
        const validation = this.validateLastNames(apellidosInput.value);
        if (validation.valid) {
          this.showFieldSuccess(apellidosInput);
        } else {
          this.showFieldError(apellidosInput, validation.message);
        }
      });

      apellidosInput.addEventListener("input", () => {
        if (apellidosInput.classList.contains("field-error")) {
          const validation = this.validateLastNames(apellidosInput.value);
          if (validation.valid) {
            this.showFieldSuccess(apellidosInput);
          }
        }
      });
    }

    // Validación en tiempo real para correo
    if (correoInput) {
      correoInput.addEventListener("blur", () => {
        const validation = this.validateEmail(correoInput.value);
        const hasContent = correoInput.value.trim().length > 0;

        if (hasContent && validation.valid) {
          this.showFieldSuccess(correoInput, validation.message);
        } else if (hasContent && !validation.valid) {
          this.showFieldError(correoInput, validation.message);
        } else {
          // Campo vacío pero opcional - limpiar validaciones
          this.clearFieldValidation(correoInput);
        }
      });

      correoInput.addEventListener("input", () => {
        // Solo validar si había un error previo y ahora tiene contenido
        if (correoInput.classList.contains("field-error")) {
          const validation = this.validateEmail(correoInput.value);
          if (validation.valid) {
            this.clearFieldValidation(correoInput);
          }
        }
      });
    }

    // Validación en tiempo real para teléfono
    if (telefonoInput) {
      telefonoInput.addEventListener("blur", () => {
        const validation = this.validatePhone(telefonoInput.value);
        if (validation.valid) {
          this.showFieldSuccess(telefonoInput, validation.message);
        } else {
          this.showFieldError(telefonoInput, validation.message);
        }
      });

      telefonoInput.addEventListener("input", () => {
        // Solo permitir números, espacios, guiones y paréntesis
        const value = telefonoInput.value;
        const filteredValue = value.replace(/[^0-9\s\-\(\)]/g, "");
        if (value !== filteredValue) {
          telefonoInput.value = filteredValue;
        }

        if (telefonoInput.classList.contains("field-error")) {
          const validation = this.validatePhone(telefonoInput.value);
          if (validation.valid) {
            this.showFieldSuccess(telefonoInput, validation.message);
          }
        }
      });
    }

    // Validación para campos de selección
    [nivelEducativo, areaConocimiento, programaInteres, plantelInteres].forEach(
      (element) => {
        if (element) {
          element.addEventListener("change", () => {
            this.clearFieldValidation(element);
          });
        }
      }
    );
  }

  validateForm() {
    const {
      nombreInput,
      apellidosInput,
      correoInput,
      telefonoInput,
      nivelEducativo,
      areaConocimiento,
      programaInteres,
      plantelInteres,
    } = this.elements;
    let isValid = true;
    this.validationErrors = {};

    // Validar nombre
    if (nombreInput) {
      const nameValidation = this.validateName(nombreInput.value);
      if (!nameValidation.valid) {
        this.showFieldError(nombreInput, nameValidation.message);
        this.validationErrors.nombre = nameValidation.message;
        isValid = false;
      } else {
        this.showFieldSuccess(nombreInput);
      }
    }

    // Validar apellidos
    if (apellidosInput) {
      const lastNameValidation = this.validateLastNames(apellidosInput.value);
      if (!lastNameValidation.valid) {
        this.showFieldError(apellidosInput, lastNameValidation.message);
        this.validationErrors.apellidos = lastNameValidation.message;
        isValid = false;
      } else {
        this.showFieldSuccess(apellidosInput);
      }
    }

    // Validar correo (opcional)
    if (correoInput) {
      const emailValidation = this.validateEmail(correoInput.value);
      // Solo mostrar error si tiene contenido Y es inválido
      if (correoInput.value.trim() && !emailValidation.valid) {
        this.showFieldError(correoInput, emailValidation.message);
        this.validationErrors.correo = emailValidation.message;
        isValid = false;
      } else if (correoInput.value.trim() && emailValidation.valid) {
        this.showFieldSuccess(correoInput, emailValidation.message);
      } else {
        // Campo vacío pero opcional - limpiar validaciones
        this.clearFieldValidation(correoInput);
      }
    }

    // Validar teléfono
    if (telefonoInput) {
      const phoneValidation = this.validatePhone(telefonoInput.value);
      if (!phoneValidation.valid) {
        this.showFieldError(telefonoInput, phoneValidation.message);
        this.validationErrors.telefono = phoneValidation.message;
        isValid = false;
      } else {
        this.showFieldSuccess(telefonoInput);
      }
    }

    // Validar nivel educativo
    if (nivelEducativo) {
      const levelValidation = this.validateEducationLevel(nivelEducativo.value);
      if (!levelValidation.valid) {
        this.showFieldError(nivelEducativo, levelValidation.message);
        this.validationErrors.nivelEducativo = levelValidation.message;
        isValid = false;
      }
    }

    // Validar área (si es requerida y visible)
    if (areaConocimiento) {
      const { areaContainer } = this.elements;
      const isAreaVisible =
        areaContainer && !areaContainer.classList.contains("hidden");

      if (isAreaVisible) {
        const areaValidation = this.validateArea(
          areaConocimiento.value,
          nivelEducativo?.value
        );
        if (!areaValidation.valid) {
          this.showFieldError(areaConocimiento, areaValidation.message);
          this.validationErrors.area = areaValidation.message;
          isValid = false;
        }
      }
    }

    // Validar programa (si es requerido y visible)
    if (programaInteres) {
      const { programaContainer } = this.elements;
      const isProgramaVisible =
        programaContainer && !programaContainer.classList.contains("hidden");

      if (isProgramaVisible) {
        const programValidation = this.validateProgram(
          programaInteres.value,
          nivelEducativo?.value,
          areaConocimiento?.value
        );
        if (!programValidation.valid) {
          this.showFieldError(programaInteres, programValidation.message);
          this.validationErrors.programa = programValidation.message;
          isValid = false;
        }
      }
    }

    // Validar plantel
    if (plantelInteres) {
      const campusValidation = this.validateCampus(plantelInteres.value);
      if (!campusValidation.valid) {
        this.showFieldError(plantelInteres, campusValidation.message);
        this.validationErrors.plantel = campusValidation.message;
        isValid = false;
      }
    }

    // Validar modalidad
    const modalityValidation = this.validateModality();
    if (!modalityValidation.valid) {
      const { modalidadContainer } = this.elements;
      if (
        modalidadContainer &&
        !modalidadContainer.classList.contains("hidden")
      ) {
        // Mostrar error en el contenedor de modalidad
        const existingError = modalidadContainer.querySelector(
          '[data-validation="error"]'
        );
        if (!existingError) {
          const errorElement = document.createElement("span");
          errorElement.className = "error-message";
          errorElement.textContent = modalityValidation.message;
          errorElement.setAttribute("data-validation", "error");
          modalidadContainer.appendChild(errorElement);
        }
      }
      this.validationErrors.modalidad = modalityValidation.message;
      isValid = false;
    }

    return isValid;
  }

  // ==========================================
  // FUNCIONES PARA APELLIDOS
  // ==========================================

  separateLastNames(fullLastName) {
    const trimmed = fullLastName.trim();
    if (!trimmed) return { paterno: "", materno: "" };

    const words = trimmed.split(/\s+/);

    if (words.length === 1) {
      return { paterno: words[0], materno: "" };
    } else if (words.length === 2) {
      return { paterno: words[0], materno: words[1] };
    } else {
      return { paterno: words[0], materno: words.slice(1).join(" ") };
    }
  }

  setupLastNameHandler() {
    const { apellidosInput, apellidoPaternoHidden, apellidoMaternoHidden } =
      this.elements;

    if (!apellidosInput || !apellidoPaternoHidden || !apellidoMaternoHidden)
      return;

    apellidosInput.addEventListener("input", () => {
      const { paterno, materno } = this.separateLastNames(apellidosInput.value);
      apellidoPaternoHidden.value = paterno;
      apellidoMaternoHidden.value = materno || "No proporcionado";
    });
  }

  // ==========================================
  // FUNCIONES PARA AUTOCOMPLETADO DE EMAIL
  // ==========================================

  showEmailSuggestions(input, suggestions) {
    const { emailSuggestions } = this.elements;
    if (!emailSuggestions) return;

    emailSuggestions.innerHTML = "";

    if (suggestions.length === 0) {
      emailSuggestions.classList.add("hidden");
      return;
    }

    suggestions.forEach((suggestion) => {
      const suggestionItem = document.createElement("div");
      suggestionItem.className =
        "px-3 py-2 cursor-pointer hover:bg-gray-100 text-sm";
      suggestionItem.textContent = suggestion;

      suggestionItem.addEventListener("click", () => {
        input.value = suggestion;
        emailSuggestions.classList.add("hidden");
        input.focus();

        const event = new Event("input", { bubbles: true });
        input.dispatchEvent(event);

        // Validar el email seleccionado
        const validation = this.validateEmail(suggestion);
        if (validation.valid) {
          this.showFieldSuccess(input, validation.message);
        }
      });

      emailSuggestions.appendChild(suggestionItem);
    });

    emailSuggestions.classList.remove("hidden");
  }

  setupEmailAutocomplete() {
    const { correoInput, emailSuggestions } = this.elements;

    if (!correoInput || !emailSuggestions) return;

    let debounceTimer;

    correoInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);

      debounceTimer = setTimeout(() => {
        const value = correoInput.value.trim();

        if (!value.includes("@") || value.split("@").length > 2) {
          emailSuggestions.classList.add("hidden");
          return;
        }

        const [username, domain] = value.split("@");

        if (!username || (domain && domain.includes("."))) {
          emailSuggestions.classList.add("hidden");
          return;
        }

        let matchedProviders = this.commonEmailProviders;

        if (domain) {
          matchedProviders = this.commonEmailProviders.filter((provider) =>
            provider.toLowerCase().startsWith(domain.toLowerCase())
          );
        }

        const suggestions = matchedProviders
          .slice(0, 6)
          .map((provider) => `${username}@${provider}`);

        this.showEmailSuggestions(correoInput, suggestions);
      }, 150);
    });

    // Ocultar sugerencias cuando se hace clic fuera
    document.addEventListener("click", (e) => {
      if (
        !correoInput.contains(e.target) &&
        !emailSuggestions.contains(e.target)
      ) {
        emailSuggestions.classList.add("hidden");
      }
    });

    // Navegación con teclado
    correoInput.addEventListener("keydown", (e) => {
      const suggestions = emailSuggestions.querySelectorAll("div");
      const activeSuggestion = emailSuggestions.querySelector(".bg-blue-100");

      if (suggestions.length === 0) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          if (!activeSuggestion) {
            suggestions[0].classList.add("bg-blue-100");
          } else {
            activeSuggestion.classList.remove("bg-blue-100");
            const next = activeSuggestion.nextElementSibling || suggestions[0];
            next.classList.add("bg-blue-100");
          }
          break;

        case "ArrowUp":
          e.preventDefault();
          if (!activeSuggestion) {
            suggestions[suggestions.length - 1].classList.add("bg-blue-100");
          } else {
            activeSuggestion.classList.remove("bg-blue-100");
            const prev =
              activeSuggestion.previousElementSibling ||
              suggestions[suggestions.length - 1];
            prev.classList.add("bg-blue-100");
          }
          break;

        case "Enter":
          if (activeSuggestion) {
            e.preventDefault();
            activeSuggestion.click();
          }
          break;

        case "Escape":
          emailSuggestions.classList.add("hidden");
          break;
      }
    });
  }

  // ==========================================
  // PROCESAMIENTO DE DATOS EDUCATIVOS
  // ==========================================

  processEducationData() {
    const processedData = {};

    for (const [nivel, contenido] of Object.entries(programasEducativos)) {
      if (!this.nivelMapping[nivel]) continue;

      const config = this.nivelMapping[nivel];
      processedData[config.key] = {
        nombre: config.nombre,
        requiereArea: config.requiereArea,
        requierePrograma: config.requierePrograma,
        areas: {},
        todosLosPlanteles: new Set(),
        todasLasModalidades: new Set(),
        todasLasIncorporaciones: new Set(),
      };

      // Procesar áreas
      for (const [area, programas] of Object.entries(contenido)) {
        processedData[config.key].areas[area] = {
          programas: {},
          planteles: new Set(),
          modalidades: new Set(),
          incorporaciones: new Set(),
        };

        // Procesar programas en cada área
        for (const [programa, planteles] of Object.entries(programas)) {
          processedData[config.key].areas[area].programas[programa] = {
            planteles: {},
            modalidades: new Set(),
            incorporaciones: new Set(),
          };

          // Procesar planteles en cada programa
          for (const [plantel, infoPlantel] of Object.entries(planteles)) {
            processedData[config.key].areas[area].programas[programa].planteles[
              plantel
            ] = {
              modalidades: [],
              incorporaciones: [],
            };

            // Procesar información de cada plantel
            infoPlantel.forEach((info) => {
              const modalidad = info.modalidad;
              const incorporacion = info.incorporacion;

              // Agregar a programa específico
              processedData[config.key].areas[area].programas[
                programa
              ].planteles[plantel].modalidades.push(modalidad);
              processedData[config.key].areas[area].programas[
                programa
              ].planteles[plantel].incorporaciones.push(incorporacion);

              // Agregar a conjuntos generales
              processedData[config.key].areas[area].planteles.add(plantel);
              processedData[config.key].areas[area].modalidades.add(modalidad);
              processedData[config.key].areas[area].incorporaciones.add(
                incorporacion
              );
              processedData[config.key].areas[area].programas[
                programa
              ].modalidades.add(modalidad);
              processedData[config.key].areas[area].programas[
                programa
              ].incorporaciones.add(incorporacion);
              processedData[config.key].todosLosPlanteles.add(plantel);
              processedData[config.key].todasLasModalidades.add(modalidad);
              processedData[config.key].todasLasIncorporaciones.add(
                incorporacion
              );
            });

            // Eliminar duplicados
            processedData[config.key].areas[area].programas[programa].planteles[
              plantel
            ].modalidades = [
              ...new Set(
                processedData[config.key].areas[area].programas[
                  programa
                ].planteles[plantel].modalidades
              ),
            ];
            processedData[config.key].areas[area].programas[programa].planteles[
              plantel
            ].incorporaciones = [
              ...new Set(
                processedData[config.key].areas[area].programas[
                  programa
                ].planteles[plantel].incorporaciones
              ),
            ];
          }

          // Convertir Sets a Arrays ordenados para programas
          processedData[config.key].areas[area].programas[
            programa
          ].modalidades = Array.from(
            processedData[config.key].areas[area].programas[programa]
              .modalidades
          ).sort();
          processedData[config.key].areas[area].programas[
            programa
          ].incorporaciones = Array.from(
            processedData[config.key].areas[area].programas[programa]
              .incorporaciones
          ).sort();
        }

        // Convertir Sets a Arrays ordenados para áreas
        processedData[config.key].areas[area].planteles = Array.from(
          processedData[config.key].areas[area].planteles
        ).sort();
        processedData[config.key].areas[area].modalidades = Array.from(
          processedData[config.key].areas[area].modalidades
        ).sort();
        processedData[config.key].areas[area].incorporaciones = Array.from(
          processedData[config.key].areas[area].incorporaciones
        ).sort();
      }

      // Convertir Sets generales a Arrays ordenados
      processedData[config.key].todosLosPlanteles = Array.from(
        processedData[config.key].todosLosPlanteles
      ).sort();
      processedData[config.key].todasLasModalidades = Array.from(
        processedData[config.key].todasLasModalidades
      ).sort();
      processedData[config.key].todasLasIncorporaciones = Array.from(
        processedData[config.key].todasLasIncorporaciones
      ).sort();
    }

    this.processedData = processedData;
  }

  // ==========================================
  // FUNCIONES AUXILIARES
  // ==========================================

  clearSelect(selectElement) {
    if (!selectElement) return;
    selectElement.innerHTML = '<option value="">Selecciona una opción</option>';
  }

  populateSelect(
    selectElement,
    options,
    placeholder = "Selecciona una opción"
  ) {
    if (!selectElement) return;

    this.clearSelect(selectElement);
    selectElement.querySelector("option").textContent = placeholder;

    options.forEach((option) => {
      const optionElement = document.createElement("option");
      optionElement.value = option;
      optionElement.textContent = option;
      selectElement.appendChild(optionElement);
    });
  }

  hideContainer(container) {
    if (container) container.classList.add("hidden");
  }

  showContainer(container) {
    if (container) container.classList.remove("hidden");
  }

  createHiddenModalidadInput(modalidad) {
    const existingHidden = this.form.querySelector(
      'input[name="modalidad"][type="hidden"]'
    );
    if (existingHidden) existingHidden.remove();

    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "modalidad";
    hiddenInput.value = modalidad;
    this.form.appendChild(hiddenInput);
  }

  createModalidadOptions(modalidades) {
    const { modalidadOptions } = this.elements;
    if (!modalidadOptions) return;

    modalidadOptions.innerHTML = "";

    modalidades.forEach((modalidad, index) => {
      const label = document.createElement("label");
      label.className = "flex items-center";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "modalidad";
      input.value = modalidad;
      input.className = "sr-only peer";
      input.required = true;
      input.id = `modalidad_${index}`;

      const span = document.createElement("span");
      span.className =
        "px-3 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-full cursor-pointer peer-checked:bg-blue-500 peer-checked:text-white peer-checked:border-blue-500 transition-colors hover:bg-gray-50";
      span.textContent = modalidad;

      label.appendChild(input);
      label.appendChild(span);
      modalidadOptions.appendChild(label);
    });
  }

  handleModalidadDisplay(modalidades, incorporaciones = []) {
    const { modalidadContainer, incorporacionHidden } = this.elements;

    if (!modalidades || modalidades.length === 0) {
      this.hideContainer(modalidadContainer);
      return;
    }

    // Actualizar incorporación si está disponible
    if (incorporaciones && incorporaciones.length > 0 && incorporacionHidden) {
      incorporacionHidden.value = incorporaciones[0];
    }

    if (modalidades.length === 1) {
      this.hideContainer(modalidadContainer);
      this.createHiddenModalidadInput(modalidades[0]);
    } else {
      const existingHidden = this.form.querySelector(
        'input[name="modalidad"][type="hidden"]'
      );
      if (existingHidden) existingHidden.remove();

      this.showContainer(modalidadContainer);
      this.createModalidadOptions(modalidades);
    }
  }

  resetDependentFields(fromLevel = "area") {
    const {
      areaConocimiento,
      areaContainer,
      programaInteres,
      programaContainer,
      plantelInteres,
      modalidadOptions,
      modalidadContainer,
      incorporacionHidden,
    } = this.elements;

    const levels = ["area", "programa", "plantel", "modalidad"];
    const startIndex = levels.indexOf(fromLevel);

    for (let i = startIndex; i < levels.length; i++) {
      switch (levels[i]) {
        case "area":
          this.clearSelect(areaConocimiento);
          this.hideContainer(areaContainer);
          if (areaConocimiento) this.clearFieldValidation(areaConocimiento);
          break;
        case "programa":
          this.clearSelect(programaInteres);
          this.hideContainer(programaContainer);
          if (programaInteres) this.clearFieldValidation(programaInteres);
          break;
        case "plantel":
          this.clearSelect(plantelInteres);
          if (plantelInteres) {
            plantelInteres.disabled = true;
            this.clearFieldValidation(plantelInteres);
          }
          break;
        case "modalidad":
          if (modalidadOptions) modalidadOptions.innerHTML = "";
          this.hideContainer(modalidadContainer);
          const existingHidden = this.form.querySelector(
            'input[name="modalidad"][type="hidden"]'
          );
          if (existingHidden) existingHidden.remove();
          if (incorporacionHidden) incorporacionHidden.value = "";
          // Limpiar errores de modalidad
          if (modalidadContainer) {
            const modalidadErrors = modalidadContainer.querySelectorAll(
              '[data-validation="error"]'
            );
            modalidadErrors.forEach((error) => error.remove());
          }
          break;
      }
    }
  }

  // ==========================================
  // INICIALIZACIÓN Y EVENT LISTENERS
  // ==========================================

  initializeNivelEducativo() {
    const { nivelEducativo } = this.elements;
    if (!nivelEducativo) return;

    const niveles = Object.keys(this.processedData);
    niveles.forEach((nivelKey) => {
      const nivel = this.processedData[nivelKey];
      const option = document.createElement("option");
      option.value = nivelKey;
      option.textContent = nivel.nombre;
      nivelEducativo.appendChild(option);
    });
  }

  setupEventListeners() {
    this.setupNivelEducativoListener();
    this.setupAreaConocimientoListener();
    this.setupProgramaInteresListener();
    this.setupPlantelInteresListener();
    this.setupFormSubmitListener();
    this.setupModalidadOptionsListener();
    this.setupLastNameHandler();
    this.setupEmailAutocomplete();
    this.setupRealTimeValidation();
  }

  setupNivelEducativoListener() {
    const { nivelEducativo, areaConocimiento, areaContainer, plantelInteres } =
      this.elements;

    if (!nivelEducativo) return;

    nivelEducativo.addEventListener("change", () => {
      const selectedLevel = nivelEducativo.value;
      this.resetDependentFields("area");

      if (!selectedLevel || !this.processedData[selectedLevel]) return;

      const nivelData = this.processedData[selectedLevel];

      if (nivelData.requiereArea) {
        const areas = Object.keys(nivelData.areas).sort();
        this.populateSelect(areaConocimiento, areas, "Selecciona un área");
        this.showContainer(areaContainer);
      } else {
        this.populateSelect(plantelInteres, nivelData.todosLosPlanteles);
        if (plantelInteres) plantelInteres.disabled = false;
      }
    });
  }

  setupAreaConocimientoListener() {
    const {
      areaConocimiento,
      nivelEducativo,
      programaInteres,
      programaContainer,
      plantelInteres,
    } = this.elements;

    if (!areaConocimiento) return;

    areaConocimiento.addEventListener("change", () => {
      const selectedArea = areaConocimiento.value;
      const selectedLevel = nivelEducativo ? nivelEducativo.value : "";

      this.resetDependentFields("programa");

      if (!selectedArea || !selectedLevel || !this.processedData[selectedLevel])
        return;

      const areaData = this.processedData[selectedLevel].areas[selectedArea];
      const nivelData = this.processedData[selectedLevel];

      if (nivelData.requierePrograma) {
        const programas = Object.keys(areaData.programas).sort();
        this.populateSelect(
          programaInteres,
          programas,
          "Selecciona un programa"
        );
        this.showContainer(programaContainer);
      } else {
        this.populateSelect(plantelInteres, areaData.planteles);
        if (plantelInteres) plantelInteres.disabled = false;
      }
    });
  }

  setupProgramaInteresListener() {
    const {
      programaInteres,
      areaConocimiento,
      nivelEducativo,
      plantelInteres,
    } = this.elements;

    if (!programaInteres) return;

    programaInteres.addEventListener("change", () => {
      const selectedPrograma = programaInteres.value;
      const selectedArea = areaConocimiento ? areaConocimiento.value : "";
      const selectedLevel = nivelEducativo ? nivelEducativo.value : "";

      this.resetDependentFields("plantel");

      if (!selectedPrograma || !selectedArea || !selectedLevel) return;

      const programaData =
        this.processedData[selectedLevel].areas[selectedArea].programas[
          selectedPrograma
        ];
      const planteles = Object.keys(programaData.planteles).sort();

      this.populateSelect(plantelInteres, planteles, "Selecciona un plantel");
      if (plantelInteres) plantelInteres.disabled = false;
    });
  }

  setupPlantelInteresListener() {
    const {
      plantelInteres,
      programaInteres,
      areaConocimiento,
      nivelEducativo,
    } = this.elements;

    if (!plantelInteres) return;

    plantelInteres.addEventListener("change", () => {
      const selectedPlantel = plantelInteres.value;
      const selectedPrograma = programaInteres ? programaInteres.value : "";
      const selectedArea = areaConocimiento ? areaConocimiento.value : "";
      const selectedLevel = nivelEducativo ? nivelEducativo.value : "";

      this.resetDependentFields("modalidad");

      if (!selectedPlantel || !selectedLevel) return;

      let modalidades = [];
      let incorporaciones = [];

      if (selectedPrograma && selectedArea) {
        const plantelData =
          this.processedData[selectedLevel].areas[selectedArea].programas[
            selectedPrograma
          ].planteles[selectedPlantel];
        modalidades = plantelData.modalidades;
        incorporaciones = plantelData.incorporaciones;
      } else if (selectedArea) {
        modalidades =
          this.processedData[selectedLevel].areas[selectedArea].modalidades;
        incorporaciones =
          this.processedData[selectedLevel].areas[selectedArea].incorporaciones;
      } else {
        modalidades = this.processedData[selectedLevel].todasLasModalidades;
        incorporaciones =
          this.processedData[selectedLevel].todasLasIncorporaciones;
      }

      this.handleModalidadDisplay(modalidades, incorporaciones);
    });
  }

  setupFormSubmitListener() {
  if (!this.form) return;

  this.form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validar formulario antes del envío
    const isFormValid = this.validateForm();

    if (!isFormValid) {
      // Scroll al primer error
      const firstError = this.form.querySelector(".field-error");
      if (firstError) {
        firstError.scrollIntoView({ behavior: "smooth", block: "center" });
        firstError.focus();
      }

      // Mostrar mensaje de error general
      console.log("❌ Formulario tiene errores:", this.validationErrors);
      return;
    }

    const formData = new FormData(this.form);

    const apellidoPaterno = this.elements.apellidoPaternoHidden?.value || "";
    const apellidoMaterno =
      this.elements.apellidoMaternoHidden?.value || "No proporcionado";

    const data = {
      nombre: formData.get("nombre") || "",
      apellido_p: apellidoPaterno,
      apellido_m: apellidoMaterno,
      correo: formData.get("correo") || "",
      telefono: formData.get("telefono") || "",
      nivel_educativo: formData.get("nivelEducativo") || "",
      plantel_interes: formData.get("plantelInteres") || "",
      programa_interes: formData.get("programaInteres") || "",
      modalidad: formData.get("modalidad") || "",
      medio: "Página web",
    };

    console.log("=== DATOS DEL FORMULARIO ===");
    console.log("Datos completos:", data);

    const submitButton = this.form.querySelector('button[type="submit"]');
    const originalText = submitButton ? submitButton.textContent : "";

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Enviando...";
    }

    const apiUrl =
      this.config.apiUrl ||
      "https://intranet.universidad-une.com/api/createleads";

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      console.log("=== RESPUESTA DEL SERVIDOR ===");
      console.log("Status:", response.status);

      if (response.ok) {
        const result = await response.json();
        console.log("✅ Respuesta exitosa:", result);

        if (result.status === "success") {
          console.log(`✅ Lead creado exitosamente. ID: ${result.lead_id}`);

          // Redirigir a página de agradecimiento
          window.location.href = "/contacto/gracias";
        } else {
          // Error reportado por el servidor
          console.warn("⚠️ Servidor reportó error:", result.message);
          this.showErrorModal(
            result.message || "Hubo un problema al procesar tu solicitud."
          );
        }
      } else {
        // Error HTTP (4xx, 5xx)
        console.error("❌ Error HTTP:", response.status, response.statusText);
        this.showErrorModal(
          `Error del servidor (${response.status}). Por favor intenta más tarde.`
        );
      }
    } catch (error) {
      // Error de red o conexión
      console.error("❌ Error de conexión:", error);
      this.showErrorModal(
        "No se pudo conectar con el servidor. Verifica tu conexión a internet e intenta nuevamente."
      );
    } finally {
      if (submitButton) {
        submitButton.textContent = originalText;
      }
    }
  });
}

// Método para mostrar el modal de error
showErrorModal(errorMessage) {
  const modal = document.getElementById("error-modal");
  const modalErrorMessage = document.getElementById("modal-error-message");
  const retryButton = document.getElementById("retry-button");
  const closeModalButton = document.getElementById("close-modal-button");

  if (!modal || !modalErrorMessage) {
    console.error("❌ Modal de error no encontrado en el DOM");
    alert(errorMessage); // Fallback
    return;
  }

  // Establecer el mensaje de error
  modalErrorMessage.textContent = errorMessage;

  // Mostrar el modal
  modal.classList.remove("hidden");

  // Agregar fondo oscuro al modal
  modal.classList.add( "bg-opacity-50");

  // Listener para el botón de reintentar
  const handleRetry = () => {
    modal.classList.add("hidden");
    // Opcional: enfocar el primer campo del formulario
    const firstInput = this.form?.querySelector("input, select");
    if (firstInput) firstInput.focus();
  };

  // Listener para el botón de cerrar
  const handleClose = () => {
    modal.classList.add("hidden");
  };

  // Remover listeners previos para evitar duplicados
  retryButton?.replaceWith(retryButton.cloneNode(true));
  closeModalButton?.replaceWith(closeModalButton.cloneNode(true));

  // Agregar nuevos listeners
  document.getElementById("retry-button")?.addEventListener("click", handleRetry);
  document.getElementById("close-modal-button")?.addEventListener("click", handleClose);

  // Cerrar modal al hacer clic fuera de él
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.add("hidden");
    }
  });
}

  clearAllValidations() {
    // Limpiar validaciones de todos los campos
    const allFields = this.form.querySelectorAll("input, select");
    allFields.forEach((field) => {
      this.clearFieldValidation(field);
    });

    // Limpiar errores de modalidad
    const { modalidadContainer } = this.elements;
    if (modalidadContainer) {
      const modalidadErrors = modalidadContainer.querySelectorAll(
        '[data-validation="error"]'
      );
      modalidadErrors.forEach((error) => error.remove());
    }

    // Resetear validationErrors
    this.validationErrors = {};
  }

  setupModalidadOptionsListener() {
    const { modalidadOptions } = this.elements;

    if (!modalidadOptions) return;

    modalidadOptions.addEventListener("click", (e) => {
      if (
        e.target.tagName === "SPAN" &&
        e.target.previousElementSibling &&
        e.target.previousElementSibling.type === "radio"
      ) {
        e.target.previousElementSibling.checked = true;

        const changeEvent = new Event("change", { bubbles: true });
        e.target.previousElementSibling.dispatchEvent(changeEvent);

        // Limpiar errores de modalidad cuando se selecciona una opción
        const { modalidadContainer } = this.elements;
        if (modalidadContainer) {
          const modalidadErrors = modalidadContainer.querySelectorAll(
            '[data-validation="error"]'
          );
          modalidadErrors.forEach((error) => error.remove());
        }
      }
    });
  }
}
