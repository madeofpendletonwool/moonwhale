FROM archlinux:latest

# Update system and install necessary dependencies
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    base-devel \
    git \
    xorg-server-xvfb \
    x11vnc \
    xterm \
    fluxbox \
    pulseaudio \
    alsa-utils \
    mesa \
    libva \
    libvdpau \
    libxrandr \
    curl \
    wget \
    dbus \
    inetutils \
    which \
    xorg-xsetroot \
    sudo

# Setup Machine ID for dbus
RUN dbus-uuidgen > /etc/machine-id

# Create a non-root user for running applications
RUN useradd -m -G wheel user && \
    echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wheel

# Create a build user for AUR packages
RUN useradd -m builder && \
    echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Clone and build Sunshine AUR package
USER builder
WORKDIR /home/builder
RUN git clone https://aur.archlinux.org/sunshine.git && \
    cd sunshine && \
    makepkg -si --noconfirm


# Switch back to root for setup
USER root

# Set up input device permissions
RUN mkdir -p /etc/udev/rules.d && \
    echo 'KERNEL=="uinput", SUBSYSTEM=="misc", GROUP="input", MODE="0660"' > /etc/udev/rules.d/99-input.rules && \
    echo 'KERNEL=="event*", SUBSYSTEM=="input", MODE="0660", GROUP="input"' >> /etc/udev/rules.d/99-input.rules && \
    echo 'KERNEL=="js*", SUBSYSTEM=="input", MODE="0660", GROUP="input"' >> /etc/udev/rules.d/99-input.rules

# Set up X11 directories with proper permissions
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Install Python and PyGame after Sunshine build to avoid rebuilding
RUN pacman -S --noconfirm \
    python \
    python-pygame \
    xorg-xinput \
    # Input-related packages
    xf86-input-evdev \
    xf86-input-libinput \
    xorg-xset \
    xorg-xrandr \
    # Debugging tools
    lsof \
    procps-ng \
    # Add udev for device rules
    udev

# Setup virtual display and audio
ENV DISPLAY=:99

# Create directories for runtime
RUN mkdir -p /home/user/.config/sunshine /home/user/apps/images /tmp/pulse /dev/input && \
    chown -R user:user /home/user && \
    # Create virtual input device if it doesn't exist
    [ -e /dev/uinput ] || mknod -m 0660 /dev/uinput c 10 223 && \
    chown root:input /dev/uinput && \
    chmod 0660 /dev/uinput

# Copy setup application
COPY --chown=user:user apps/setup.py /home/user/apps/setup.py
COPY --chown=user:user apps/images/moonwhale.jpg /home/user/apps/images/moonwhale.jpg
RUN chmod +x /home/user/apps/setup.py

# Copy configuration files
COPY --chown=user:user sunshine.conf /home/user/.config/sunshine/sunshine.conf
COPY --chown=user:user apps.json /home/user/.config/sunshine/apps.json
COPY --chown=user:user startup.sh /home/user/startup.sh
RUN chmod +x /home/user/startup.sh

# Switch to the non-root user
USER user
WORKDIR /home/user

# Expose required ports
EXPOSE 47984-47990/tcp
EXPOSE 48010/tcp
EXPOSE 47998-48000/udp
EXPOSE 48002/udp
EXPOSE 5900/tcp

ENTRYPOINT ["/home/user/startup.sh"]
